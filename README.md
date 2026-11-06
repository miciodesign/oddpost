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

Campi del front matter oltre a quelli base: `tema` (animali, scienza, record, mondo, oggetti; genera le pagine
`/tema/<slug>/` e sceglie le storie correlate), `seo_title` (title per Google, con il nome ricercabile),
`meta_description` (descrizione per Google), `in_breve_dove` / `in_breve_cosa` / `in_breve_perche`
(il riquadro "in breve" in cima al pezzo), `image_query` (due parole chiave in inglese: in fase di build,
GitHub Actions cerca una foto su Pixabay e la scarica in `static/img/articoli/<slug>.jpg`; non serve scaricarla
a mano, basta la chiave di ricerca) e `image_alt` (descrizione dell'immagine in italiano). Il modello li spiega tutti.

Le immagini si scaricano solo in CI (serve `PIXABAY_API_KEY` nei secret del repo GitHub), perché questa sandbox
non può raggiungere pixabay.com: in locale `python3 build.py` genera il sito senza immagini nuove, usa quelle
già in `static/img/articoli/` se presenti.

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
