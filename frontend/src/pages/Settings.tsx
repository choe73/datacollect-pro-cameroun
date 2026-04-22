import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Save, Database, Bell, Shield } from 'lucide-react'

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Paramètres</h1>
        <p className="text-muted-foreground">
          Configurer les options de l'application
        </p>
      </div>

      {/* Database Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            Base de données
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="retention">Durée de rétention (jours)</Label>
            <Input id="retention" type="number" defaultValue={180} />
            <p className="text-xs text-muted-foreground">
              Les données brutes plus anciennes seront automatiquement archivées
            </p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Auto-cleanup</Label>
              <p className="text-xs text-muted-foreground">
                Supprimer automatiquement les données obsolètes
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Alertes collecte</Label>
              <p className="text-xs text-muted-foreground">
                Recevoir des notifications sur l'état des collectes
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>Alertes système</Label>
              <p className="text-xs text-muted-foreground">
                Recevoir des alertes en cas de problème système
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Sécurité
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Rate limiting</Label>
              <p className="text-xs text-muted-foreground">
                Limiter les requêtes pour éviter les abus
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="grid gap-2">
            <Label htmlFor="api-key">Clé API</Label>
            <div className="flex gap-2">
              <Input id="api-key" type="password" value="sk-************************" readOnly />
              <Button variant="outline">Régénérer</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button className="bg-cm-green hover:bg-cm-green/90">
          <Save className="w-4 h-4 mr-2" />
          Enregistrer les modifications
        </Button>
      </div>
    </div>
  )
}
