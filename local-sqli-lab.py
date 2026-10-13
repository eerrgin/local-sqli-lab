python

from pathlib import Path
import zipfile

PROJECT = Path("local-sqli-lab")

FILES = {
    "README.md": r"""
# Local SQL Injection Lab

Eğitim amacıyla hazırlanmış, yalnızca yerel örnek veritabanı
kullanan bir uygulama güvenliği laboratuvarı.

## Amaç
- SQL sorgularında güvensiz string birleştirmeyi incelemek
- Kaynak kodda riskli sorgu oluşturma biçimini tespit etmek
- Parametreli sorguyla düzeltmeyi doğrulamak
- Bulguları tekrarlanabilir testlerle belgelemek

## Gereksinimler
Python 3.10 veya üzeri. Harici paket gerekmez.

## Çalıştırma

```bash
python scanner.py
python -m unittest discover -s tests -v
```

## Kapsam ve güvenlik

Bu proje sadece kendi içindeki örnek Python dosyalarını ve
geçici SQLite veritabanını kullanır. Ağ bağlantısı kurmaz,
uzak hedef taramaz ve gerçek kullanıcı verisi içermez.

`vulnerable_demo.py` bilerek hatalı yazılmış eğitim örneğidir.
Bu dosya üretim uygulamalarında kullanılmamalıdır.

## Teknik bulgu

Örnek koddaki kullanıcı girdisi SQL sorgusuna string
birleştirmeyle eklenmektedir. Bu tasarım, girdinin SQL
sözdizimini etkilemesine neden olabilir.

Düzeltme: SQL sorgusunu parametre yer tutucularıyla yazmak
ve kullanıcı girdisini ayrı parametre olarak geçirmek.

## Sınırlamalar

`scanner.py` basit bir eğitim tarayıcısıdır; tam bir statik
analiz aracı değildir. Yanlış pozitif ve yanlış negatif
sonuçlar üretebilir. Bir bulgunun gerçek uygulamadaki
etkisi ayrıca doğrulanmalıdır.

## Lisans

MIT
""".strip() + "\n",

    "vulnerable_demo.py": r'''
"""Bilerek güvensiz eğitim örneği. Üretimde kullanmayın."""

def build_query(username: str) -> str:
    # LAB BULGUSU: Kullanıcı girdisi SQL metnine birleştiriliyor.
    return "SELECT id, username FROM users WHERE username = '" + username + "'"
'''.strip() + "\n",

    "fixed_demo.py": r'''
"""Güvenli sorgu oluşturma örneği."""

def build_query():
    # Değer SQL metninden ayrı bir parametre olarak gönderilir.
    return "SELECT id, username FROM users WHERE username = ?", ()
'''.strip() + "\n",

    "scanner.py": r'''
"""Yalnızca proje içindeki eğitim örneğini inceleyen basit tarayıcı."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "vulnerable_demo.py"

def scan(path: Path):
    findings = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if "return " in line and "SELECT " in line and " + " in line:
            findings.append({
                "file": path.name,
                "line": number,
                "severity": "Medium (educational estimate)",
                "title": "SQL sorgusunda string birleştirme",
                "evidence": line.strip(),
                "recommendation": "Parametreli SQL sorgusu kullanın."
            })
    return findings

if __name__ == "__main__":
    results = scan(TARGET)
    print("Local SQL Injection Lab - Source Review")
    print("Scope:", TARGET.name)
    if not results:
        print("Eşleşme bulunmadı. Bu, kodun güvenli olduğunu kanıtlamaz.")
    for item in results:
        print(f"\n[{item['severity']}] {item['title']}")
        print(f"Dosya: {item['file']}:{item['line']}")
        print(f"Kanıt: {item['evidence']}")
        print("Öneri:", item["recommendation"])
    print("\nNot: Bu basit tarama kesin güvenlik hükmü vermez.")
'''.strip() + "\n",

    "tests/test_lab.py": r'''
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scanner import scan

class LabTests(unittest.TestCase):
    def test_detects_intentionally_unsafe_example(self):
        findings = scan(ROOT / "vulnerable_demo.py")
        self.assertTrue(findings)
        self.assertIn("SQL sorgusunda string birleştirme",
                      findings[0]["title"])

    def test_fixed_example_uses_parameter_placeholder(self):
        source = (ROOT / "fixed_demo.py").read_text(encoding="utf-8")
        self.assertIn("WHERE username = ?", source)
        self.assertNotIn(" + username", source)

if __name__ == "__main__":
    unittest.main()
'''.strip() + "\n",

    "REPORT.md": r"""
# Güvenlik Bulgu Raporu

## Başlık
SQL sorgusunun kullanıcı girdisiyle string birleştirme yoluyla oluşturulması

## Test kapsamı
Yalnızca bu depodaki `vulnerable_demo.py` adlı eğitim dosyası.
Gerçek bir hizmet veya üçüncü taraf hedef test edilmemiştir.

## Durum
Bilerek oluşturulmuş laboratuvar bulgusu. Gerçek bir sistemde
keşfedilmiş güvenlik açığı olarak sunulmamalıdır.

## Teknik açıklama
SQL sorgusuna güvenilmeyen girdinin doğrudan eklenmesi, girdinin
veri olarak kalması yerine sorgunun yapısını etkileyebilmesine yol
açabilir. Gerçek etki; kullanılan sürücüye, sorguya ve uygulama
bağlamına bağlıdır.

## Kanıt
`python scanner.py` komutu, eğitim dosyasındaki sorgu
birleştirme örneğini satır numarasıyla raporlar.

## Etki değerlendirmesi
Bu laboratuvar, tasarım riskini gösterir. Gerçek bir uygulamanın
etkilenebilir olduğunu veya veri açığa çıktığını kanıtlamaz.

## Düzeltme
`fixed_demo.py` dosyasındaki gibi parametreli sorgu kullanın.
Girdileri SQL metnine birleştirmeyin.

## Doğrulama
`python -m unittest discover -s tests -v`

## Sonuç
Bu test, belirli bir kod örneğindeki riskli deseni gösterir.
Tam uygulama güvenliği değerlendirmesinin yerine geçmez.
""".strip() + "\n",

    "SECURITY.md": r"""
# Security Policy

Bu depo, yalnızca yerel ve yapay eğitim örnekleri içerir.

Bu projedeki bir hata veya yanlışlık için GitHub Issues üzerinden
bildirim açabilirsiniz. Lütfen gerçek kişilere ait veri, parola,
gizli anahtar veya üçüncü taraf sistemlere ait hassas bilgi eklemeyin.

Bu proje, gerçek hedeflere karşı test yapılmasına izin vermez veya
böyle bir yetki verildiği anlamına gelmez.
""".strip() + "\n",

    "LICENSE": r"""
MIT License

Copyright (c) 2026 Project Author

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files, to deal
in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, subject to inclusion
of this copyright notice and permission notice.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
""".strip() + "\n",

    ".gitignore": """
__pycache__/
*.py[cod]
.venv/
.env
""".lstrip()
}

def main():
    PROJECT.mkdir(exist_ok=True)
    for name, content in FILES.items():
        target = PROJECT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    archive = Path("local-sqli-lab.zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in PROJECT.rglob("*"):
            if path.is_file():
                zf.write(path, path.as_posix())

    print("Proje klasörü:", PROJECT.resolve())
    print("ZIP dosyası:", archive.resolve())
    print("Dosya sayısı:", len(FILES))

if __name__ == "__main__":
    main()