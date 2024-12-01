# Popis Malware

Jedná se o ransomware, který nejdříve zasílá soubory typu `.txt`, `.docx`, `.pdf`, `.tmp`, `.log` na REST API, poté tyto soubory zašifruje. Samotný výběr souborů je doplněn o biologicky inspirovaný algoritmus, konkrétně genetický algoritmus, s cílem vybrat co nejlepší podmnožinu (pořadí) souborů pro odeslání, na základě jejich poměru ku důležitosti (typ, umístění atd.) a velikosti.

## Kompletní popis programu

### Popis funkcionality

#### 1. Sběr souborů a jejich hodnocení

**Funkce `calculate_importance(file_path)`**  
Hodnotí důležitost souborů podle několika kritérií:

- **Přípona souboru**:  
  Soubory jako `.txt`, `.docx` nebo `.pdf` mají vyšší prioritu, zatímco `.tmp` nebo `.log` mají nižší.
- **Velikost souboru**:  
  Soubory menší než 1 MB jsou považovány za důležitější, zatímco soubory větší než 10 MB mají nižší prioritu.
- **Datum poslední úpravy**:  
  Čerstvě upravené soubory mají vyšší důležitost než ty staré.
- **Klíčová slova**:  
  Pokud název souboru obsahuje slova jako `report`, `invoice` nebo `important`, získává vyšší hodnocení.
- **Umístění souboru**:  
  Soubory v `Documents` nebo `Desktop` mají vyšší prioritu, naopak soubory v `Temp` nebo `Cache` mají nižší prioritu.

#### 2. Genetický algoritmus pro výběr souborů

**Cíl:** Vybrat kombinaci souborů, která maximalizuje důležitost a zároveň minimalizuje celkovou velikost.

**Hlavní kroky:**
- **Inicializace populace**:  
  Náhodně generuje binární chromozomy (1 = soubor vybrán, 0 = soubor nevýběr).
- **Fitness funkce**:  
  Vyhodnocuje kvalitu chromozomů na základě celkové důležitosti a penalizace za velikost.
- **Výběr rodičů**:  
  Pomocí ruletového výběru jsou vybíráni rodiče k vytvoření nových chromozomů.
- **Crossover (křížení)**:  
  Kombinuje části dvou rodičů a vytváří nové potomky.
- **Mutace**:  
  Náhodně obrací bity v chromozomu s danou pravděpodobností, aby byla zajištěna rozmanitost.
- **Výsledek**:  
  Po skončení generací algoritmus vrátí nejlepší kombinaci souborů.

#### 3. Šifrování souborů

**Funkce `encrypt_file_on_disk(file_path, key)`**  
- Šifruje obsah vybraných souborů pomocí klíče Fernet.
- Přepíše soubor na disku zašifrovanou verzí.

#### 4. Asynchronní odesílání dat na REST API

**Asynchronní funkce `send_file_data_to_api(payload, api_url)`**  
- Posílá JSON payload obsahující:
  - Identifikátor zařízení (UID).
  - IP adresu zařízení.
  - Obsah souboru (před šifrováním).
  - Stav operace (např. `starting`, `running`, `completed`).
- Pokud API odpoví chybovým stavem, zobrazí chybu.

#### 5. Hlavní workflow

**Funkce `main()`**  
- Inicializuje šifrovací klíč.
- Získává identifikátor zařízení a IP adresu.
- Odesílá úvodní stav (`starting`) na API.
- Prochází zadanou složku (`start_path`), vybírá soubory podle genetického algoritmu a postupně:
  - Šifruje soubory.
  - Odesílá jejich obsah na API.
- Po dokončení odesílá závěrečný stav (`completed`) na API.
