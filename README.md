# Taxi Soesi Gent

Website van Taxi Soesi, Gent, 24 uur op 24 bereikbaar op 0470 53 41 24.

## Pagina's

- `index.html` — de website: ritprijs berekenen van adres tot adres, VIP-luchthaventransfer,
  zakelijk aanbod, vaste ritprijzen, boeken via WhatsApp.
- `zakelijk.html` — de pagina voor bedrijven, met offerteformulier per e-mail.

Beide bestanden staan op zichzelf: opmaak, scripts, foto en de adreslijst
(25.911 straten tot 40 km rond Gent, uit het Belgische adresregister) zitten erin.
Er is geen build nodig en geen API-sleutel.

## Wat u snel kunt aanpassen

Bovenaan het `<script>`-blok van `index.html`:

| Naam | Betekenis |
| --- | --- |
| `WA_NUMBER` | het WhatsApp-nummer |
| `BASE` | € 15 voor de eerste kilometers |
| `INCL_KM` | 3 km inbegrepen |
| `PER_KM` | € 2,60 per bijkomende kilometer |
| `FIXED` | de vaste prijzen per bestemming |

In `zakelijk.html` staat bovenaan `MAIL`, vandaag Novaracommv@gmail.com, het adres waar het offerteformulier naartoe gaat.

## Online zetten

Settings → Pages → Branch `main`, map `/ (root)` → Save.
De site staat dan op https://elyasseoulzrag1-droid.github.io/taxisoesigent/
