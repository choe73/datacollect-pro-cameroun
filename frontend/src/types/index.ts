// Common Types
export interface Dataset {
  id: number
  name: string
  description?: string
  source: string
  domain: string
  row_count: number
  columns: string[]
  last_updated: string
  created_at: string
  schema: Record<string, string>
  metadata?: Record<string, unknown>
}

export interface DatasetStats {
  dataset_id: number
  total_rows: number
  numeric_columns: string[]
  categorical_columns: string[]
  date_columns: string[]
  null_counts: Record<string, number>
  memory_usage_mb: number
}

// Analysis Types
export interface RegressionRequest {
  dataset_id: number
  target_column: string
  feature_columns: string[]
  test_size?: number
  method: 'linear' | 'ridge' | 'lasso' | 'elasticnet' | 'polynomial'
  polynomial_degree?: number
  alpha?: number
  l1_ratio?: number
}

export interface RegressionResult {
  intercept: number
  coefficients: Array<{
    name: string
    value: number
    std_error?: number
    t_statistic?: number
    p_value?: number
    ci_lower?: number
    ci_upper?: number
    vif?: number
  }>
  metrics: {
    r2_score: number
    adjusted_r2?: number
    rmse: number
    mae: number
    mse: number
  }
  diagnostics: {
    durbin_watson?: number
    high_vif_features: string[]
  }
  predictions: number[]
  residuals: number[]
  plot_data?: Record<string, unknown>
  method: string
  warning_messages: string[]
}

export interface PCARequest {
  dataset_id: number
  columns: string[]
  n_components?: number
  standardize?: boolean
  method?: 'kaiser' | 'variance_80' | 'all'
}

export interface PCAResult {
  n_components: number
  components: Array<{
    component_number: number
    eigenvalue: number
    variance_explained_pct: number
    cumulative_variance_pct: number
    loadings: Record<string, number>
  }>
  explained_variance: {
    ratios: number[]
    cumulative: number[]
  }
  plot_data?: Record<string, unknown>
}

export interface ClassificationRequest {
  dataset_id: number
  target_column: string
  feature_columns: string[]
  algorithm: 'logistic' | 'svm' | 'random_forest' | 'gradient_boosting' | 'knn' | 'naive_bayes'
  test_size?: number
  cv_folds?: number
}

export interface ClassificationResult {
  algorithm: string
  overall_metrics: {
    accuracy: number
    precision: number
    recall: number
    f1_score: number
    roc_auc?: number
  }
  class_metrics: Array<{
    class_name: string
    precision: number
    recall: number
    f1_score: number
    support: number
  }>
  confusion_matrix: {
    labels: string[]
    matrix: number[][]
    normalized_matrix?: number[][]
  }
  feature_importances?: Record<string, number>
  best_params?: Record<string, unknown>
}

export interface ClusteringRequest {
  dataset_id: number
  columns: string[]
  algorithm: 'kmeans' | 'dbscan' | 'hierarchical' | 'gmm' | 'spectral'
  n_clusters?: number
  eps?: number
  min_samples?: number
  method?: 'elbow' | 'silhouette' | 'auto'
}

export interface ClusteringResult {
  algorithm: string
  n_clusters: number
  clusters: Array<{
    cluster_id: number
    size: number
    centroid: number[]
    individuals: number[]
  }>
  metrics: {
    silhouette_score: number
    calinski_harabasz_score?: number
    davies_bouldin_score?: number
  }
  plot_data?: Record<string, unknown>
}

// Collection Types
export interface DataSource {
  id: string
  name: string
  url: string
  status: string
  last_update?: string
}

export interface CollectionTask {
  task_id: string
  source: string
  status: 'pending' | 'running' | 'completed' | 'failed'
}

// UI Types
export interface NavItem {
  label: string
  href: string
  icon: string
}

export interface Toast {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
}
