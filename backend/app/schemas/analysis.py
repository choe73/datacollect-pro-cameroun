"""Analysis request and response schemas."""

from typing import Dict, List, Optional, Literal, Any, Union
from pydantic import BaseModel, Field, validator


# Base Analysis Request
class AnalysisRequest(BaseModel):
    """Base schema for analysis requests."""

    dataset_id: int = Field(..., gt=0)
    columns: List[str] = Field(..., min_items=1)


# Descriptive Analysis
class DescriptiveRequest(AnalysisRequest):
    """Request for descriptive statistics."""

    confidence_level: float = Field(0.95, ge=0.8, le=0.99)


class DescriptiveResult(BaseModel):
    """Result of descriptive analysis."""

    column: str
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    missing_count: int
    unique_count: int


class CorrelationMatrix(BaseModel):
    """Correlation matrix result."""

    columns: List[str]
    values: List[List[float]]
    p_values: Optional[List[List[float]]] = None
    method: str = "pearson"


class DescriptiveAnalysisResponse(BaseModel):
    """Complete descriptive analysis response."""

    statistics: List[DescriptiveResult]
    correlations: Optional[CorrelationMatrix] = None
    plot_data: Optional[Dict[str, Any]] = None


# Regression Analysis
class RegressionRequest(BaseModel):
    """Request for regression analysis."""

    dataset_id: int = Field(..., gt=0)
    target_column: str = Field(..., min_length=1)
    feature_columns: List[str] = Field(..., min_items=1)
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    method: Literal["linear", "ridge", "lasso", "elasticnet", "polynomial"] = "linear"
    polynomial_degree: Optional[int] = Field(None, ge=2, le=5)
    alpha: float = Field(1.0, ge=0.0)  # For regularization
    l1_ratio: float = Field(0.5, ge=0.0, le=1.0)  # For ElasticNet

    @validator("polynomial_degree")
    def validate_polynomial_degree(cls, v, values):
        if values.get("method") == "polynomial" and v is None:
            raise ValueError("polynomial_degree required for polynomial regression")
        return v


class RegressionMetrics(BaseModel):
    """Regression metrics."""

    r2_score: float
    adjusted_r2: Optional[float] = None
    rmse: float
    mae: float
    mse: float
    f_statistic: Optional[float] = None
    f_pvalue: Optional[float] = None


class CoefficientInfo(BaseModel):
    """Coefficient information."""

    name: str
    value: float
    std_error: Optional[float] = None
    t_statistic: Optional[float] = None
    p_value: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    vif: Optional[float] = None


class RegressionDiagnostics(BaseModel):
    """Regression diagnostics."""

    durbin_watson: Optional[float] = None
    jarque_bera_stat: Optional[float] = None
    jarque_bera_pvalue: Optional[float] = None
    residuals_normality: Optional[str] = None
    heteroscedasticity: Optional[str] = None
    high_vif_features: List[str] = Field(default_factory=list)


class RegressionResult(BaseModel):
    """Complete regression result."""

    intercept: float
    coefficients: List[CoefficientInfo]
    metrics: RegressionMetrics
    diagnostics: RegressionDiagnostics
    predictions: List[float] = Field(default_factory=list)
    residuals: List[float] = Field(default_factory=list)
    actual_values: List[float] = Field(default_factory=list)
    plot_data: Optional[Dict[str, Any]] = None
    method: str
    warning_messages: List[str] = Field(default_factory=list)


# PCA Analysis
class PCARequest(BaseModel):
    """Request for PCA analysis."""

    dataset_id: int = Field(..., gt=0)
    columns: List[str] = Field(..., min_items=2)
    n_components: Optional[int] = Field(None, ge=1)
    standardize: bool = True
    method: Literal["kaiser", "variance_80", "all"] = "kaiser"


class PCAComponent(BaseModel):
    """PCA component information."""

    component_number: int
    eigenvalue: float
    variance_explained_pct: float
    cumulative_variance_pct: float
    loadings: Dict[str, float]


class PCAIndividual(BaseModel):
    """Individual projection in PCA."""

    id: int
    coordinates: List[float]
    cos2: List[float]
    contribution: List[float]


class PCAResult(BaseModel):
    """Complete PCA result."""

    n_components: int
    components: List[PCAComponent]
    individuals: List[PCAIndividual]
    correlation_circle: Optional[Dict[str, Any]] = None
    scree_plot_data: Dict[str, Any]
    biplot_data: Optional[Dict[str, Any]] = None
    explained_variance: Dict[str, List[float]]


# Classification Analysis
class ClassificationRequest(BaseModel):
    """Request for classification."""

    dataset_id: int = Field(..., gt=0)
    target_column: str = Field(..., min_length=1)
    feature_columns: List[str] = Field(..., min_items=1)
    algorithm: Literal[
        "logistic", "svm", "random_forest", "gradient_boosting", "knn", "naive_bayes"
    ] = "logistic"
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    cv_folds: int = Field(5, ge=2, le=10)
    hyperparameters: Optional[Dict[str, Any]] = None


class ClassificationMetrics(BaseModel):
    """Classification metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    log_loss: Optional[float] = None


class ClassMetrics(BaseModel):
    """Per-class metrics."""

    class_name: str
    precision: float
    recall: float
    f1_score: float
    support: int


class ConfusionMatrix(BaseModel):
    """Confusion matrix."""

    labels: List[str]
    matrix: List[List[int]]
    normalized_matrix: Optional[List[List[float]]] = None


class ClassificationResult(BaseModel):
    """Complete classification result."""

    algorithm: str
    overall_metrics: ClassificationMetrics
    class_metrics: List[ClassMetrics]
    confusion_matrix: ConfusionMatrix
    roc_curve_data: Optional[Dict[str, Any]] = None
    feature_importances: Optional[Dict[str, float]] = None
    grid_search_results: Optional[Dict[str, Any]] = None
    best_params: Optional[Dict[str, Any]] = None
    cross_validation_scores: Optional[List[float]] = None


# Clustering Analysis
class ClusteringRequest(BaseModel):
    """Request for clustering."""

    dataset_id: int = Field(..., gt=0)
    columns: List[str] = Field(..., min_items=2)
    algorithm: Literal["kmeans", "dbscan", "hierarchical", "gmm", "spectral"] = "kmeans"
    n_clusters: Optional[int] = Field(None, ge=2, le=20)
    eps: Optional[float] = Field(None, ge=0.01, le=10.0)  # For DBSCAN
    min_samples: Optional[int] = Field(None, ge=2, le=50)  # For DBSCAN
    method: Literal["elbow", "silhouette", "auto"] = "auto"


class ClusterInfo(BaseModel):
    """Cluster information."""

    cluster_id: int
    size: int
    centroid: List[float]
    individuals: List[int]
    intra_cluster_distance: Optional[float] = None


class ClusteringMetrics(BaseModel):
    """Clustering quality metrics."""

    silhouette_score: float
    calinski_harabasz_score: Optional[float] = None
    davies_bouldin_score: Optional[float] = None
    inertia: Optional[float] = None  # For K-Means


class OptimalKResult(BaseModel):
    """Optimal K determination result."""

    method: str
    optimal_k: int
    scores: Dict[str, List[float]]
    plot_data: Dict[str, Any]


class ClusteringResult(BaseModel):
    """Complete clustering result."""

    algorithm: str
    n_clusters: int
    clusters: List[ClusterInfo]
    metrics: ClusteringMetrics
    optimal_k_analysis: Optional[OptimalKResult] = None
    elbow_plot_data: Optional[Dict[str, Any]] = None
    silhouette_plot_data: Optional[Dict[str, Any]] = None
    cluster_visualization: Optional[Dict[str, Any]] = None
