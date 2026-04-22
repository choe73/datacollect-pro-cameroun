import { useQuery } from '@tanstack/react-query'
import { getDatasets } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Database, Search, Filter } from 'lucide-react'
import type { Dataset } from '@/types'

export function Datasets() {
  const { data: datasets, isLoading } = useQuery<Dataset[]>({
    queryKey: ['datasets'],
    queryFn: getDatasets,
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Datasets</h1>
          <p className="text-muted-foreground">
            Explorer et gérer les données disponibles
          </p>
        </div>
        <Button className="bg-cm-green hover:bg-cm-green/90">
          <Database className="w-4 h-4 mr-2" />
          Importer un dataset
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Rechercher un dataset..." className="pl-9" />
            </div>
            <div className="flex gap-2">
              <Select>
                <SelectTrigger className="w-[180px]">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Domaine" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="agriculture">Agriculture</SelectItem>
                  <SelectItem value="sante">Santé</SelectItem>
                  <SelectItem value="education">Éducation</SelectItem>
                  <SelectItem value="economie">Économie</SelectItem>
                </SelectContent>
              </Select>
              <Select>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Source" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  <SelectItem value="world_bank">World Bank</SelectItem>
                  <SelectItem value="open_data">Open Data Cameroun</SelectItem>
                  <SelectItem value="nasa">NASA POWER</SelectItem>
                  <SelectItem value="fao">FAO</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Datasets Grid */}
      {isLoading ? (
        <div className="text-center py-8">Chargement...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {datasets?.map((dataset) => (
            <Card key={dataset.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{dataset.name}</CardTitle>
                    <p className="text-xs text-muted-foreground mt-1">
                      {dataset.source}
                    </p>
                  </div>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-cm-green/10 text-cm-green">
                    {dataset.domain}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Lignes</p>
                    <p className="font-medium">{dataset.row_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Colonnes</p>
                    <p className="font-medium">{dataset.columns.length}</p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    Mis à jour: {new Date(dataset.last_updated).toLocaleDateString('fr-FR')}
                  </p>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Voir
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Analyser
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
