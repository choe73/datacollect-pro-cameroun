import { useQuery } from '@tanstack/react-query'
import { checkHealth } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Database, Brain, Cloud } from 'lucide-react'

export function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const stats = [
    {
      title: 'Datasets',
      value: '47',
      description: 'Total datasets disponibles',
      icon: Database,
      color: 'bg-blue-500',
    },
    {
      title: 'Analyses',
      value: '128',
      description: 'Analyses complétées',
      icon: Activity,
      color: 'bg-green-500',
    },
    {
      title: 'Modèles ML',
      value: '12',
      description: 'Modèles entraînés',
      icon: Brain,
      color: 'bg-purple-500',
    },
    {
      title: 'Collectes',
      value: '24',
      description: 'Collectes ce mois',
      icon: Cloud,
      color: 'bg-cm-yellow',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground">
          Vue d'ensemble de la plateforme DataCollect Pro Cameroun
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-full ${stat.color}`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle>État du système</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Statut général</span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                health?.status === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {health?.status === 'healthy' ? 'Opérationnel' : 'Problème détecté'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Base de données</span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                health?.services?.database === 'healthy'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health?.services?.database === 'healthy' ? 'Connectée' : 'Déconnectée'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Cache Redis</span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                health?.services?.redis === 'healthy'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health?.services?.redis === 'healthy' ? 'Connecté' : 'Déconnecté'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Dernières collectes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">World Bank API</p>
                  <p className="text-xs text-muted-foreground">Il y a 2 heures</p>
                </div>
                <span className="text-xs text-green-600">Succès</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">NASA POWER (Météo)</p>
                  <p className="text-xs text-muted-foreground">Il y a 5 heures</p>
                </div>
                <span className="text-xs text-green-600">Succès</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">FAO FAOSTAT</p>
                  <p className="text-xs text-muted-foreground">Il y a 1 jour</p>
                </div>
                <span className="text-xs text-green-600">Succès</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Modèles récents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Régression Prix Agricoles</p>
                  <p className="text-xs text-muted-foreground">R² = 0.992</p>
                </div>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                  Actif
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">K-Means Régions</p>
                  <p className="text-xs text-muted-foreground">Silhouette = 0.82</p>
                </div>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                  Actif
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Classification Santé</p>
                  <p className="text-xs text-muted-foreground">Accuracy = 0.945</p>
                </div>
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                  Entraînement
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
