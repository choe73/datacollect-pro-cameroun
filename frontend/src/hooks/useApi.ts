"""Custom hooks for API operations."""

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getDatasets,
  getDataset,
  getSources,
  triggerCollection,
  triggerAllCollections,
  descriptiveAnalysis,
  regressionAnalysis,
  pcaAnalysis,
  classificationAnalysis,
  clusteringAnalysis,
} from '@/lib/api'
import type {
  Dataset,
  DataSource,
  DescriptiveRequest,
  RegressionRequest,
  PCARequest,
  ClassificationRequest,
  ClusteringRequest,
} from '@/types'

// Datasets hooks
export function useDatasets() {
  return useQuery<Dataset[]>({
    queryKey: ['datasets'],
    queryFn: getDatasets,
  })
}

export function useDataset(id: number) {
  return useQuery<Dataset>({
    queryKey: ['datasets', id],
    queryFn: () => getDataset(id),
    enabled: !!id,
  })
}

// Data sources hooks
export function useDataSources() {
  return useQuery<{ sources: DataSource[] }>({
    queryKey: ['sources'],
    queryFn: getSources,
  })
}

// Collection hooks
export function useTriggerCollection() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (sourceId: string) => triggerCollection(sourceId, false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })
}

export function useTriggerAllCollections() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: () => triggerAllCollections(false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
    },
  })
}

// Analysis hooks
export function useDescriptiveAnalysis() {
  return useMutation({
    mutationFn: (data: DescriptiveRequest) => descriptiveAnalysis(data),
  })
}

export function useRegressionAnalysis() {
  return useMutation({
    mutationFn: (data: RegressionRequest) => regressionAnalysis(data),
  })
}

export function usePCAAnalysis() {
  return useMutation({
    mutationFn: (data: PCARequest) => pcaAnalysis(data),
  })
}

export function useClassificationAnalysis() {
  return useMutation({
    mutationFn: (data: ClassificationRequest) => classificationAnalysis(data),
  })
}

export function useClusteringAnalysis() {
  return useMutation({
    mutationFn: (data: ClusteringRequest) => clusteringAnalysis(data),
  })
}
