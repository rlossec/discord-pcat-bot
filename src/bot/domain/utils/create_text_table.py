

def create_text_table(data_rows: list[dict], columns: dict[str, str]) -> str:
    """Crée un tableau de texte formaté pour un bloc de code Discord (Markdown)"""
    
    # Calculer la largeur maximale de chaque colonne
    col_widths = {col: len(col) for col in columns.keys()}
    
    for row in data_rows:
        for col_key, col_title in columns.items():
            value = str(row.get(col_key, ''))
            col_widths[col_key] = max(col_widths[col_key], len(value))
            
    # Ajouter un peu de marge
    col_widths = {k: v + 2 for k, v in col_widths.items()}
    
    # Création de l'en-tête et du séparateur
    header = " | ".join(col_title.ljust(col_widths[col_key]) for col_key, col_title in columns.items())
    separator = " | ".join("-" * col_widths[col_key] for col_key in columns.keys())
    
    # Ajout des lignes de données
    table_content = f"{header}\n{separator}\n"
    for row in data_rows:
        line = " | ".join(str(row.get(col_key, '')).ljust(col_widths[col_key]) for col_key in columns.keys())
        table_content += f"{line}\n"
        
    return table_content.strip()
