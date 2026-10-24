# Oddpost — strano ma vero, ogni giorno

Sito statico di [oddpost.it](https://oddpost.it). Gli articoli sono file Markdown in `content/`,
il generatore `build.py` li trasforma nel sito pronto in `public/`.

## Come si aggiunge un articolo

1. Copia `content/_modello-articolo.md` in `content/storie/` (o `content/oggetti/`)
   con nome `AAAA-MM-GG-titolo-breve.md`.
2. Compila i campi in cima al file e scrivi il pezzo sotto.
3. Fai commit e push su `main`. In un paio di minuti GitHub ricostruisce il sito
   nel ramo `deploy` e Hostinger lo pubblica.

Un articolo con `draft: true` non viene pubblicato.

## Struttura

- `content/storie/` — rubrica "Storie strane ma vere"
- `content/oggetti/` — rubrica "Oggetti assurdi che esistono davvero" (link affiliati)
- `content/pagine/` — pagine fisse (Chi siamo, Contatti, Privacy, Affiliazioni)
- `templates/` — i modelli HTML (Jinja2)
- `static/` — foglio di stile, immagini
- `build.py` — il generatore
- `.github/workflows/build.yml` — costruisce e pubblica nel ramo `deploy`

## Provare in locale

```bash
pip install -r requirements.txt
python3 build.py
python3 -m http.server 8000 --directory public
```

Poi apri http://localhost:8000.

## Pubblicazione

Hostinger (hPanel → sito → Avanzate → Git) è collegato al ramo `deploy` di questo repository.
Nel ramo `deploy` c'è solo il sito generato, mai i sorgenti.
