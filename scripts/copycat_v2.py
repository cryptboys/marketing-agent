"""
Copycat Engine v2 — pola engagement tinggi dari @NenkMonica
Input: raw berita → Output: 3 varian post siap pakai + validation
"""

import json, os, re, sys
from datetime import datetime
sys.path.append('scripts')
from pipeline import load_voice_profile, validate_content, check_anti_slop

TEMPLATES = {
    "shock_fact": {
        "name": "Fakta + Emosi",
        "desc": "Data mengejutkan + komentar sinis",
        "pattern": "[FAKTA]. [REAKSI]",
        "examples": ["Harga sewa jet pribadi anak presiden Rp 308jt/jam. Betul-betul keluarga ndeso yang sederhana."]
    },
    "question_hook": {
        "name": "Hook Pertanyaan",
        "desc": "Pertanyaan retoris yang bikin mikir",
        "pattern": "[PERTANYAAN]? [KONTEKS].",
        "examples": ["Apakah anda SETUJU???", "Akankah anda menganggap orang yg punya banyak utang ke anda menjadi spesial?"]
    },
    "contrast": {
        "name": "Kontras",
        "desc": "Atas vs Bawah, Kata vs Nyata",
        "pattern": "[X] ... [Y] ... DISTORSI",
        "examples": ["Pidato Presiden Menyanjung Para Buruh. Aparat di bawah Menggebuk Aksi Para Buruh. Atas dan Bawah ada distorsi."]
    },
    "wajib_viral": {
        "name": "WAJIB VIRAL",
        "desc": "Pembukaan WAJIB VIRAL + narasi ironi",
        "pattern": "WAJIB VIRAL\n[NARASI IRONI].\n[REAKSI]",
        "examples": ["WAJIB VIRAL\nAnak-anak di sekolah dpt makan gratis dg menu alakadarnya seharga 10rb.\nKetika pulang ke rumah didapati org tuanya sdg menangis krn terkena PHK. Sungguh miris Negeri ini."]
    },
    "one_word_hook": {
        "name": "Kata Kunci + Emosi",
        "desc": "Satu kata kuat + subtitle emosional",
        "pattern": "[KATA KUNCI] : [SUB]",
        "examples": ["DERITA di tengah PENDERITAAN", "Epic Moment.", "Mata Elang Netizen sangat jeli melebih penyelidik."]
    },
    "data_dump": {
        "name": "Data Binner",
        "desc": "Data/info keras tanpa hiasan",
        "pattern": "[DATA 1]\n[DATA 2]\n[KOMENTAR]",
        "examples": ["Anggota DPR dpt tunjangan Perumahan Rp 50jt/bln. Rakyat dpt Potongan Perumahan 3%/bln dari gajinya."]
    }
}

def detect_template(text):
    """Match raw news ke template paling cocok"""
    text_lower = text.lower()
    
    # Cek kata kunci
    has_data = bool(re.search(r'\d+', text))
    has_question_words = any(w in text_lower for w in ['apa', 'apakah', 'kenapa', 'mengapa', 'bagaimana', 'siapa'])
    has_numbers_with_units = bool(re.search(r'[\d,.]+ *(rb|jt|m|%|\$|rp)', text_lower))
    has_contrast_words = any(w in text_lower for w in ['tetapi', 'namun', 'sedangkan', 'sementara', 'padahal'])
    has_irony_candidates = any(w in text_lower for w in ['aneh', 'miris', 'ironis', 'gila', 'edan', 'parah'])
    
    if has_numbers_with_units and has_irony_candidates:
        return "shock_fact"
    elif has_data and has_contrast_words:
        return "contrast"
    elif has_data and has_question_words:
        return "question_hook"
    elif has_data:
        return "data_dump"
    elif has_irony_candidates:
        return "wajib_viral"
    else:
        return "one_word_hook"

def generate_post(news_title, news_summary, template_name, our_voice):
    """Generate LLM prompt based on template pattern"""
    
    tmpl = TEMPLATES[template_name]
    
    prompt = f"""Kamu adalah content creator dengan gaya @NenkMonica — emosional, sinis, pake kata-kata keras, ALL CAPS untuk penekanan.
Voice kamu: {our_voice}

BERITA:
Judul: {news_title}
Isi: {news_summary}

TEMPLATE: {tmpl['name']}
Pola: {tmpl['pattern']}
Contoh: {tmpl['examples'][0]}

TUGAS:
1. Tulis ulang berita di atas menggunakan template {tmpl['name']}
2. Gaya: emosional, sinis, pake ALL CAPS buat kata kunci
3. Max 280 karakter
4. Pake bahasa Indonesia campur Inggris sehari-hari
5. Sertakan hook di awal yang bikin orang berhenti scroll
6. Akhiri dengan reaksi/pendapat yang strong

OUTPUT (JSON):
{{
  "content": "text post max 280 chars",
  "hook_type": "{template_name}",
  "target_emotion": "marah|miris|tertawa|simpati"
}}
"""
    return prompt

def generate_variants(news_title, news_summary, our_voice, n=3):
    """Generate N variants, each dengan template berbeda"""
    templates = list(TEMPLATES.keys())
    variants = []
    
    for i in range(min(n, len(templates))):
        tmpl = templates[i]
        prompt = generate_post(news_title, news_summary, tmpl, our_voice)
        variants.append({
            "template": tmpl,
            "prompt": prompt,
            "status": "pending_llm"
        })
    return variants

def mock_llm_reply(variant):
    """Simulasi output LLM — nanti diganti real LLM call"""
    mock_responses = {
        "shock_fact": "Harga Jet Pribadi Anak Presiden Rp 308,8 JUTA/JAM. Harga sewa jet pribadi Gulfstream G650 mulai 13,000 dolar AS per jam. Rakyat? Tidur di kolong jembatan. Betul-betul KELUARGA NDESO.",
        "question_hook": "Apakah lo tau berapa duit rakyat yang dipake buat sewa jet pribadi anak presiden? Rp 308,8 juta per jam. Per JAM, bre. Sementara rakyat di bawah demo minta harga BBM diturunin.",
        "contrast": "Anak Presiden sewa jet pribadi Rp 308jt/jam.\nMasyarakat di daerah demo naik angkot.\nAtas dan Bawah ada DISTORSI.",
        "wajib_viral": "WAJIB VIRAL\nAnak Presiden naik jet pribadi Gulfstream G650. Sewa Rp 308jt per jam.\nKata mereka: keluarga sederhana.\nKenyataannya: keluarga yang jualan gaya.",
        "one_word_hook": "JET PRIBADI.\nRp 308,8 JUTA/JAM.\nSiapa bilang ini negara merdeka?",
        "data_dump": "Harga sewa jet pribadi Gulfstream G650: 13,000 dolar AS/jam.\nRp 308,8 juta/jam.\nAnak Presiden.\nRakyat:\nNo comments.",
    }
    content = mock_responses.get(variant["template"], "Error generating content")
    return {
        "content": content,
        "hook_type": variant["template"],
        "target_emotion": "marah"
    }

def run_copycat_v2(news_title, news_summary, our_voice):
    """Full pipeline: generate variants → validate → rank"""
    print("=== COPYCAT ENGINE V2 ===\n")
    
    # Deteksi template otomatis dari berita
    best_template = detect_template(news_summary)
    print(f"[DETECT] Template cocok: {best_template} ({TEMPLATES[best_template]['name']})\n")
    
    # Generate 3 variants
    variants = generate_variants(news_title, news_summary, our_voice)
    print(f"[GEN] {len(variants)} variants generated\n")
    
    results = []
    for i, v in enumerate(variants):
        print(f"[{i+1}/{len(variants)}] Template: {v['template']}")
        
        # Simulasi LLM
        llm_out = mock_llm_reply(v)
        content = llm_out["content"]
        print(f"  Content: {content}\n")
        
        # Validate
        article = {"link": "https://news.google.com/rss/articles/jetpribadi", "summary": news_summary + " " + content}
        validation = validate_content(content, article, our_voice)
        
        status = "✓ PASS" if validation["all_passed"] else "✗ FAIL"
        print(f"  Validation: {status}")
        for check, result in validation["checks"].items():
            s = "✓" if result["passed"] else "✗"
            print(f"    {s} {check}: {result['message']}")
        
        # Save
        today = datetime.now().strftime("%Y-%m-%d")
        out_dir = f"vault/content/{today}"
        os.makedirs(out_dir, exist_ok=True)
        
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', news_title[:30])
        fname = f"copycat_v2_{v['template']}_{safe_title}.md"
        fpath = os.path.join(out_dir, fname)
        
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(f"# Variant {i+1}: {v['template']}\n\n")
            f.write(f"**Status:** {'READY' if validation['all_passed'] else 'NEEDS REVIEW'}\n\n")
            f.write(f"## Content\n```\n{content}\n```\n\n")
            f.write(f"## Source\n{news_title}\n\n")
            f.write(f"## Validation\n```json\n{json.dumps(validation, indent=2)}\n```\n")
        
        print(f"  Saved: {fpath}\n")
        
        results.append({
            "variant": i+1,
            "template": v["template"],
            "content": content,
            "validation_passed": validation["all_passed"],
            "file": fpath
        })
    
    # Rank
    passed = [r for r in results if r["validation_passed"]]
    print(f"\n=== SUMMARY ===")
    print(f"Total: {len(results)}, Passed: {len(passed)}, Failed: {len(results)-len(passed)}")
    for r in results:
        status = "✓" if r["validation_passed"] else "✗"
        print(f"  {status} [{r['template']}] {r['content'][:60]}...")
    
    return results

if __name__ == '__main__':
    news_title = "Harga Sewa Jet Pribadi Anak Presiden Rp 308,8 Juta/Jam"
    news_summary = "Harga sewa jet pribadi Gulfstream G650 berkisar antara 13.000 dolar AS hingga 19.750 dolar AS per jam. Kalau dikonversi dalam rupiah dengan kurs 15.636 per dolar AS, setara Rp 308,8 juta per jam."
    voice = load_voice_profile()
    results = run_copycat_v2(news_title, news_summary, voice)
