Dette programmet inneholder hovedfunksjonen
`analyser(<filnavn.xlsx>, default_sheet='Sheet0')`

For å kjøre programmet, installer pakken med
pip install HC_salgsanalyse

## Bruke pakken i et script
Deretter, skriv og kjør et enkelt script som

from salgsanalyse import analyser
`analyser(<filnavn.xlsx>, default_sheet='Sheet0')`

Merk at argumentet 'default_sheet' er valgfritt.

## Fra terminalen/kommandolinjen

Alternativt kan du åpne terminalen og skrive

`python -m salgsanalyse`

eller

`python -m salgsanalyse <filnavn.xlsx>`

eller

`python -m salgsanalyse <filnavn.xlsx> <arknavn>`

## Ekstra funksjonalitet

I tilegg er funksjonen `merge(<file1>, <sheet1>, <file2>, <sheet2>, <target_file>, <target_sheet>)` definert for å slå sammen filer.
Filen <target_file> trenger ikke eksistere fra før av, men opprettes når du slår sammen filene <file1> og <file2>