![SpotagLogo](https://raw.githubusercontent.com/alex-m00n/Spotag/main/spotag.png)
# 🎵 Spotag - Spotify NFC pour PC

Une application Python qui permet d'ouvrir des liens Spotify sur votre PC via un NFC scanné avec votre téléphone

## ✨ Fonctionnalités

- **Interface graphique moderne** avec design inspiré de Spotify
- **Serveur web local** pour recevoir les liens depuis des tags NFC scanné avec votre téléphone
- **Conversion de liens Spotify en lien Spotag** directement depuis l'interface
- **Contrôle du serveur** (démarrage/arrêt)
- **Configuration sauvegardée** automatiquement

## 📱 Utilisation

### Interface graphique

L'application s'ouvre avec une interface moderne comprenant :

1. **Contrôle du Serveur**
   - Bouton "Démarrer le Serveur" pour activer le serveur web
   - Bouton "Arrêter le Serveur" pour le désactiver
   - Affichage de l'URL du serveur (par défaut : `http://192.0.0.1:5000/spotify`soit `http://localhost:5000/spotify`)

2. **Conversion de Liens Spotify en liens Spotag**
   - Zone de saisie pour entrer un lien Spotify (https://open.spotify.com/playlist/Abcde12345)
   - Zone de sortie en lien Spotag (http://192.0.0.1:5000/spotify?link=spotify:playlisty:Abcde12345)

### Utilisation avec NFC

1. **Démarrez le serveur** depuis l'interface
2. **Contertissez votre URL Spotify en URL Spotag** depuis l'interface :
   ```
   URL Spotify : https://open.spotify.com/playlist/Abcde12345
   ```
   ```
   URL Spotag : http://192.0.0.1:5000/spotify?link=spotify:playlisty:Abcde12345
   ```
3. **Créez des tags NFC** contenant des URLs au format :
   ```
   http://192.0.0.1:5000/spotify?link=spotify:playlist:Abcde12345
   ```
4. **Scannez les tags** avec votre téléphone pour ouvrir automatiquement les morceaux sur votre ordinateur


## 🔧 Personnalisation

### Changer le port du serveur
Modifiez la valeur `server_port` dans le fichier `spotify_nfc_config.json` :
```json
{
  "server_port": 5000, //5000 par défaut
  ...
}
```

## 🐛 Dépannage

### Le serveur ne démarre pas
- Vérifiez qu'aucune autre application n'utilise le port 5000
- Changez le port dans la configuration
- Vérifiez que le pare-feu autorise l'application

### Les liens ne s'ouvrent pas
- Vérifiez que vous avez un navigateur par défaut configuré
- Assurez-vous que les liens Spotify sont valides
- Vérifiez votre connexion internet


## 🤝 Contribution

N'hésitez pas à contribuer en :
- Signalant des bugs
- Proposant de nouvelles fonctionnalités
- Améliorant l'interface utilisateur


**Développé avec ❤️ par AlexM00n**
