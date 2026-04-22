import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Brain, Play, Download, Trash2, CheckCircle } from 'lucide-react'

export function Models() {
  const models = [
    {
      id: 1,
      name: 'Régression Prix Agricoles',
      type: 'regression',
      algorithm: 'Linear Regression',
      metrics: { r2: 0.992, rmse: 12.5 },
      status: 'active',
      created_at: '2024-03-15',
    },
    {
      id: 2,
      name: 'K-Means Régions',
      type: 'clustering',
      algorithm: 'K-Means',
      metrics: { silhouette: 0.82, n_clusters: 5 },
      status: 'active',
      created_at: '2024-03-10',
    },
    {
      id: 3,
      name: 'Classification Santé',
      type: 'classification',
      algorithm: 'Random Forest',
      metrics: { accuracy: 0.945, f1: 0.938 },
      status: 'training',
      created_at: '2024-03-20',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Modèles ML</h1>
          <p className="text-muted-foreground">
            Gérer les modèles entraînés et leurs prédictions
          </p>
        </div>
        <Button className="bg-cm-green hover:bg-cm-green/90">
          <Brain className="w-4 h-4 mr-2" />
          Entraîner un nouveau modèle
        </Button>
      </div>

      {/* Models List */}
      <div className="grid gap-4">
        {models.map((model) => (
          <Card key={model.id}>
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-cm-green/10 flex items-center justify-center">
                    <Brain className="w-6 h-6 text-cm-green" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">{model.name}</h3>
                      {model.status === 'active' ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Actif
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="animate-pulse">
                          Entraînement...
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {model.algorithm} • {model.type}
                    </p>
                    <div className="flex gap-4 mt-2 text-sm">
                      {model.metrics.r2 !== undefined && (
                        <span>R² = {model.metrics.r2}</span>
                      )}
                      {model.metrics.accuracy !== undefined && (
                        <span>Accuracy = {model.metrics.accuracy}</span>
                      )}
                      {model.metrics.silhouette !== undefined && (
                        <span>Silhouette = {model.metrics.silhouette}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Play className="w-4 h-4 mr-2" />
                    Prédire
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Exporter
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
