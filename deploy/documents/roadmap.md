# Roadmap

---

## New Ideas
* How to do literature review on a set of papers? 
  * extract key research topics 
  * identity hierarchy in literature: e.g. marketing strategy / consumer (brand) equity

* How to evaluate citations? 
  * given context, quantity the usefulness of a reference

## TODO

* Spell check? Extracted text recognition is not perfect.
* Try OpenAI language model
* Fine-tuning?
* How to leverage citation & reference data?

## Citation & Reference

We have metadata for all focal paper (in the list of papers), reference, citation (top 1K by their citation count), and
their reference.

Metadata comes from Elsevier, Semantic Scholar, and CrossRef. They include title, authors, DOI, abstract, keywords,
subject fields.

| Item                         | Count      |
|------------------------------|------------|
| Paper (Focal)                | 447        | 
| Linked Citation (Secondary)  | 151,369    |
| Linked Reference (Secondary) | 23,359     |
| Reference of Reference       | 819,673    |
| Reference of Citation        | 11,464,684 |

## Fine-Tuning

* Which model to tune?
* Need to balance local runtime (RAM size, w/o GPU) and accuracy
* May require labor intense labeling
