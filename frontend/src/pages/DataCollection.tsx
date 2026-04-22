import { useQuery, useMutation } from '@tanstack/react-query'
import { getSources, triggerCollection, triggerAllCollections, getCollectionStatus } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { CloudDownload, Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import type { DataSource } from '@/types'

export function DataCollection() {
  const { toast } = useToast()
  const { data: sources, isLoading } = useQuery<DataSource[]>({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  const collectMutation = useMutation({
    mutationFn: (sourceId: string) => triggerCollection(sourceId, false),
    onSuccess: (data) => {
      toast({
        title: 'Collecte démarrée',
        description: `Tâche ID: ${data.task_id}`,
      })
    },
    onError: () => {
      toast({
        title: 'Erreur',
        description: 'Impossible de démarrer la collecte',
        variant: 'destructive',
      })
    },
  })

  const collectAllMutation = useMutation({
    mutationFn: () => triggerAllCollections(false),
    onSuccess: () => {
      toast({
        title: 'Collecte globale démarrée',
        description: 'Toutes les sources sont en cours de collecte',
      })
    },
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'unavailable':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'collecting':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Collecte de données</h1>
          <p className="text-muted-foreground">
            Gérer les sources de données et les collectes automatiques
          </p>
        </div>
        <Button 
          className="bg-cm-green hover:bg-cm-green/90"
          onClick={() => collectAllMutation.mutate()}
          disabled={collectAllMutation.isPending}
        >
          <CloudDownload className="w-4 h-4 mr-2" />
          {collectAllMutation.isPending ? 'Collecte en cours...' : 'Collecter toutes les sources'}
        </Button>
      </div>

      {/* Sources Grid */}
      {isLoading ? (
        <div className="text-center py-8">Chargement...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources?.sources.map((source) => (
            <Card key={source.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(source.status)}
                    <div>
                      <CardTitle className="text-lg">{source.name}</CardTitle>
                      <p className="text-xs text-muted-foreground">{source.url}</p>
                    </div>
                  </div>
                  <Badge variant={source.status === 'available' ? 'default' : 'secondary'}>
                    {source.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Dernière mise à jour:
                    </p>
                    <p className="text-sm">
                      {source.last_update 
                        ? new Date(source.last_update).toLocaleString('fr-FR')
                        : 'Jamais'}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => collectMutation.mutate(source.id)}
                    disabled={collectMutation.isPending || source.status !== 'available'}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Collecter
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Collection History */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des collectes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">World Bank API</p>
                  <p className="text-xs text-muted-foreground">Il y a 2 heures</p>
                </div>
              </div>
              <Badge variant="outline">1,245 enregistrements</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">NASA POWER (Météo)</p>
                  <p className="text-xs text-muted-foreground">Il y a 5 heures</p>
                </div>
              </div>
              <Badge variant="outline">8,760 enregistrements</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
