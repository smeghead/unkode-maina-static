## migration to static site.

## retrieve original contents.

```bash
wget \
  --mirror \
  --convert-links \
  --adjust-extension \
  --page-requisites \
  --no-parent \
  --no-host-directories \
  --span-hosts \
  --domains unkode-mania.net \
  --reject-regex 'search|\\?s=' \
  https://unkode-mania.net/
```


```bash
wget \
  --input-file=content-links.txt \
  --convert-links \
  --adjust-extension \
  --page-requisites \
  --no-host-directories \
  --span-hosts \
  --domains unkode-mania.net \
  --no-clobber
```
