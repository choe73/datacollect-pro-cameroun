import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { BarChart3, LineChart, PieChart, Activity } from 'lucide-react'
import { getDatasets } from '@/lib/api'
import type { Dataset } from '@/types'

export function Analysis() {
  const [selectedDataset, setSelectedDataset] = useState<string>('')
  const { data: datasets } = useQuery<Dataset[]>({
    queryKey: ['datasets'],
    queryFn: getDatasets,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analyse de données</h1>
        <p className="text-muted-foreground">
          Effectuer des analyses statistiques et des modèles ML
        </p>
      </div>

      {/* Dataset Selection */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <span className="text-sm font-medium">Dataset:</span>
            <Select value={selectedDataset} onValueChange={setSelectedDataset}>
              <SelectTrigger className="w-full sm:w-[300px]">
                <SelectValue placeholder="Sélectionner un dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets?.map((dataset) => (
                  <SelectItem key={dataset.id} value={String(dataset.id)}>
                    {dataset.name} ({dataset.row_count.toLocaleString()} lignes)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Types */}
      <Tabs defaultValue="descriptive" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
          <TabsTrigger value="descriptive">
            <BarChart3 className="w-4 h-4 mr-2" />
            Descriptive
          </TabsTrigger>
          <TabsTrigger value="regression">
            <LineChart className="w-4 h-4 mr-2" />
            Régression
          </TabsTrigger>
          <TabsTrigger value="pca">
            <PieChart className="w-4 h-4 mr-2" />
            ACP
          </TabsTrigger>
          <TabsTrigger value="classification">
            <Activity className="w-4 h-4 mr-2" />
            Classification
          </TabsTrigger>
          <TabsTrigger value="clustering">
            <BarChart3 className="w-4 h-4 mr-2" />
            Clustering
          </TabsTrigger>
        </TabsList>

        <TabsContent value="descriptive">
          <Card>
            <CardHeader>
              <CardTitle>Analyse descriptive</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Sélectionnez un dataset pour commencer l'analyse descriptive.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="regression">
          <Card>
            <CardHeader>
              <CardTitle>Régression linéaire</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Configurez les variables pour la régression.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pca">
          <Card>
            <CardHeader>
              <CardTitle>Analyse en Composantes Principales</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Réduction de dimensionnalité par ACP.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="classification">
          <Card>
            <CardHeader>
              <CardTitle>Classification supervisée</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Entraînez des modèles de classification.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="clustering">
          <Card>
            <CardHeader>
              <CardTitle>Clustering non supervisé</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Découvrez les patterns cachés dans vos données.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
