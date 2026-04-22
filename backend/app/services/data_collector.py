"""Data collection service for external APIs."""

import httpx
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.raw_data import RawData
from app.models.processed_data import ProcessedData


class WorldBankCollector:
    """Collector for World Bank Open Data API."""
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    # Key indicators for Cameroon
    INDICATORS = {
        "SP.POP.TOTL": "Population totale",
        "SP.POP.GROW": "Croissance démographique",
        "NY.GDP.MKTP.CD": "PIB (USD)",
        "NY.GDP.PCAP.CD": "PIB par habitant",
        "AG.LND.FRST.ZS": "Forêt (% terres)",
        "SE.PRM.ENRR": "Scolarisation primaire",
        "SE.SEC.ENRR": "Scolarisation secondaire",
        "SH.DYN.MORT": "Mortalité infantile",
        "SH.STA.BASS.ZS": "Accès assainissement",
        "SH.H2O.BASW.ZS": "Accès eau potable",
        "EG.ELC.ACCS.ZS": "Accès électricité",
        "IS.ROD.DNST.K2": "Densité routière",
        "AG.PRD.FOOD.XD": "Production alimentaire",
        "FP.CPI.TOTL.ZG": "Inflation",
        "SL.UEM.TOTL.ZS": "Chômage",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def collect_all_indicators(
        self,
        country_code: str = "CMR",
        start_year: int = 2000,
        end_year: int = 2023,
    ) -> Dict[str, Any]:
        """Collect all World Bank indicators for a country."""
        results = {
            "source": "world_bank",
            "country": country_code,
            "records_collected": 0,
            "indicators_processed": 0,
            "errors": [],
        }
        
        for indicator_code, indicator_name in self.INDICATORS.items():
            try:
                data = await self._fetch_indicator(
                    indicator_code, country_code, start_year, end_year
                )
                
                if data:
                    # Store raw data
                    await self._store_raw_data(
                        source="world_bank",
                        dataset_name=f"wb_{indicator_code}",
                        data={
                            "indicator": indicator_code,
                            "indicator_name": indicator_name,
                            "country": country_code,
                            "data": data,
                        },
                    )
                    
                    # Process and store structured data
                    for item in data:
                        if item.get("value") is not None:
                            await self._store_processed_data(
                                domain="economy" if "GDP" in indicator_code or "FP.CPI" in indicator_code 
                                      else "health" if "SH." in indicator_code
                                      else "education" if "SE." in indicator_code
                                      else "environment" if "AG.LND" in indicator_code or "EG." in indicator_code
                                      else "demography",
                                indicator=indicator_name,
                                date_value=datetime(int(item["date"]), 1, 1),
                                numeric_value=float(item["value"]),
                                metadata={
                                    "indicator_code": indicator_code,
                                    "country": country_code,
                                },
                            )
                    
                    results["records_collected"] += len(data)
                    results["indicators_processed"] += 1
                    
            except Exception as e:
                results["errors"].append({
                    "indicator": indicator_code,
                    "error": str(e),
                })
        
        return results
    
    async def _fetch_indicator(
        self,
        indicator: str,
        country: str,
        start_year: int,
        end_year: int,
    ) -> List[Dict[str, Any]]:
        """Fetch a specific indicator from World Bank API."""
        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}"
        params = {
            "date": f"{start_year}:{end_year}",
            "format": "json",
            "per_page": 100,
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        # World Bank returns [metadata, data] format
        if len(data) > 1:
            return data[1]
        return []
    
    async def _store_raw_data(
        self,
        source: str,
        dataset_name: str,
        data: Dict[str, Any],
    ) -> None:
        """Store raw collected data."""
        # Generate hash for deduplication
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Check if already exists
        query = select(RawData).where(RawData.hash == data_hash)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            return
        
        raw_data = RawData(
            source=source,
            dataset_name=dataset_name,
            data=data,
            hash=data_hash,
            status="processed",
        )
        self.db.add(raw_data)
        await self.db.commit()
    
    async def _store_processed_data(
        self,
        domain: str,
        indicator: str,
        date_value: datetime,
        numeric_value: float,
        metadata: Dict[str, Any],
    ) -> None:
        """Store processed data."""
        processed = ProcessedData(
            domain=domain,
            indicator=indicator,
            date_value=date_value,
            numeric_value=numeric_value,
            metadata=metadata,
        )
        self.db.add(processed)
        await self.db.commit()


class NASAPowerCollector:
    """Collector for NASA POWER meteorological data API."""
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Parameters for Cameroon
    PARAMETERS = [
        "PRECTOTCORR",  # Precipitation
        "T2M",          # Temperature at 2 meters
        "RH2M",         # Relative humidity at 2 meters
        "WS10M",        # Wind speed at 10 meters
        "ALLSKY_SFC_SW_DWN",  # Solar radiation
    ]
    
    REGIONS = {
        "yaounde": {"lat": 3.8480, "lon": 11.5021},
        "douala": {"lat": 4.0511, "lon": 9.7679},
        "garoua": {"lat": 9.3014, "lon": 13.3971},
        "bamenda": {"lat": 5.9597, "lon": 10.1453},
        "maroua": {"lat": 10.5910, "lon": 14.3159},
        "bafoussam": {"lat": 5.4778, "lon": 10.4176},
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def collect_meteo_data(
        self,
        start_date: str = "20200101",
        end_date: str = "20231231",
    ) -> Dict[str, Any]:
        """Collect meteorological data for all regions."""
        results = {
            "source": "nasa_power",
            "records_collected": 0,
            "regions_processed": 0,
            "errors": [],
        }
        
        for region_name, coords in self.REGIONS.items():
            try:
                data = await self._fetch_region_data(
                    coords["lat"],
                    coords["lon"],
                    start_date,
                    end_date,
                )
                
                if data and "properties" in data:
                    parameters = data["properties"].get("parameter", {})
                    dates = list(parameters.get(self.PARAMETERS[0], {}).keys())
                    
                    for date_str in dates:
                        meteo_data = {
                            "date": date_str,
                            "region": region_name,
                            "lat": coords["lat"],
                            "lon": coords["lon"],
                        }
                        
                        for param in self.PARAMETERS:
                            param_data = parameters.get(param, {})
                            meteo_data[param] = param_data.get(date_str)
                        
                        # Store data
                        await self._store_meteo_data(meteo_data)
                        results["records_collected"] += 1
                    
                    results["regions_processed"] += 1
                    
            except Exception as e:
                results["errors"].append({
                    "region": region_name,
                    "error": str(e),
                })
        
        return results
    
    async def _fetch_region_data(
        self,
        lat: float,
        lon: float,
        start: str,
        end: str,
    ) -> Dict[str, Any]:
        """Fetch data for a specific region."""
        url = self.BASE_URL
        params = {
            "parameters": ",".join(self.PARAMETERS),
            "community": "RE",
            "longitude": lon,
            "latitude": lat,
            "start": start,
            "end": end,
            "format": "JSON",
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def _store_meteo_data(self, data: Dict[str, Any]) -> None:
        """Store meteorological data."""
        date_str = data["date"]
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        
        processed = ProcessedData(
            domain="meteo",
            indicator="meteo_data",
            region=data["region"],
            date_value=datetime(year, month, day),
            numeric_value=data.get("T2M", 0),
            metadata={
                "precipitation": data.get("PRECTOTCORR"),
                "humidity": data.get("RH2M"),
                "wind_speed": data.get("WS10M"),
                "solar_radiation": data.get("ALLSKY_SFC_SW_DWN"),
                "lat": data["lat"],
                "lon": data["lon"],
            },
        )
        self.db.add(processed)
        await self.db.commit()


class FAOCollector:
    """Collector for FAO FAOSTAT data API."""
    
    BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en/data"
    
    # Cameroon country code
    COUNTRY_CODE = "45"  # Cameroon
    
    # Key datasets
    DATASETS = {
        "QCL": "Production",  # Crops and Livestock Products
        "RL": "Land Use",     # Land Use
        "QAD": "Prices",      # Prices
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def collect_agricultural_data(
        self,
        years: List[int] = None,
    ) -> Dict[str, Any]:
        """Collect FAO agricultural data."""
        if years is None:
            years = list(range(2010, 2024))
        
        results = {
            "source": "fao",
            "records_collected": 0,
            "datasets_processed": 0,
            "errors": [],
        }
        
        for dataset_code, dataset_name in self.DATASETS.items():
            try:
                data = await self._fetch_dataset(
                    dataset_code,
                    self.COUNTRY_CODE,
                    years,
                )
                
                if data and "data" in data:
                    for item in data["data"]:
                        await self._store_fao_data(item, dataset_name)
                        results["records_collected"] += 1
                    
                    results["datasets_processed"] += 1
                    
            except Exception as e:
                results["errors"].append({
                    "dataset": dataset_code,
                    "error": str(e),
                })
        
        return results
    
    async def _fetch_dataset(
        self,
        dataset_code: str,
        country_code: str,
        years: List[int],
    ) -> Dict[str, Any]:
        """Fetch a specific FAO dataset."""
        url = f"{self.BASE_URL}/{dataset_code}"
        
        payload = {
            "area": [country_code],
            "years": [str(y) for y in years],
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    async def _store_fao_data(self, item: Dict[str, Any], dataset_name: str) -> None:
        """Store FAO data."""
        year = int(item.get("year", 2020))
        
        processed = ProcessedData(
            domain="agriculture",
            indicator=f"fao_{dataset_name}",
            date_value=datetime(year, 1, 1),
            numeric_value=float(item.get("value", 0)) if item.get("value") else 0,
            metadata={
                "item": item.get("item"),
                "element": item.get("element"),
                "unit": item.get("unit"),
                "dataset": dataset_name,
            },
        )
        self.db.add(processed)
        await self.db.commit()
