#!/usr/bin/env python3
import os
import glob
import re

# Catálogo optimizado de genes marcadores para Listeria monocytogenes
GENES_INTERES = {
    # Isla de Patogenicidad 1 (LIPI-1) y reguladores
    "prfA": "Regulador maestro de virulencia",
    "hly": "Listeriolisina O (LLO) - Toxina específica",
    "actA": "Proteína de polimerización de actina",
    "plcA": "Fosfolipasa A",
    "plcB": "Fosfolipasa B",
    
    # Invasinas (Internalinas)
    "inlA": "Internalina A",
    "inlB": "Internalina B",
    "inlC": "Internalina C",
    "inlJ": "Internalina J",
    
    # Marcadores de Exclusividad de Especie (No dependientes de virulencia)
    "lmo0733": "Internalin-like protein",
    "lmo0113": "Permeasa PTS específica de beta-glucósido",
    "lmo2122": "Componente de permeasa PTS específico de L. monocytogenes",
    
    # Marcador de Género (Listeria spp.)
    "prs": "Fosforribosilpirofosfato sintetasa"
}

# Mapeo de Locus Tags por si el GTF usa los IDs en lugar de nombres comunes
LOCUS_TAGS = {
    "lmo0200": "plcA", "lmo0201": "prfA", "lmo0202": "hly", 
    "lmo0203": "mpl",  "lmo0204": "actA", "lmo0205": "plcB", # LIPI-1 completado
    "lmo0433": "inlA", "lmo0434": "inlB",
    "lmo0733": "lmo0733", "lmo0113": "lmo0113", "lmo2122": "lmo2122",
    "lmo0199": "prs"
}

def parse_gtf_attributes(attributes_str):
    """Extrae un diccionario con los atributos clave del GTF."""
    attributes = {}
    matches = re.findall(r'(\w+)\s+"([^"]*)"', attributes_str)
    for key, value in matches:
        attributes[key] = value
    return attributes

def process_file(filepath):
    results = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
                
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
            
            # Analizamos nivel CDS para evitar duplicaciones
            feature_type = parts[2]
            if feature_type != "CDS":
                continue
                
            try:
                coverage = float(parts[-1])
            except ValueError:
                continue
                
            # Filtro: Cobertura estrictamente mayor a 0
            if coverage <= 0.0:
                continue
                
            attributes = parse_gtf_attributes(parts[8])
            gene_name = attributes.get("gene", "")
            locus_tag = attributes.get("locus_tag", "")
            
            # Normalizar el nombre del gen si vino por Locus Tag
            if not gene_name and locus_tag in LOCUS_TAGS:
                gene_name = LOCUS_TAGS[locus_tag]
            elif locus_tag in LOCUS_TAGS and LOCUS_TAGS[locus_tag] in GENES_INTERES:
                gene_name = LOCUS_TAGS[locus_tag]
                
            # Si el gen mapeado está en nuestra lista de interés, lo guardamos
            if gene_name in GENES_INTERES:
                results.append({
                    "gene": gene_name,
                    "locus_tag": locus_tag,
                    "coverage": coverage,
                    "description": GENES_INTERES[gene_name]
                })
    return results

def main():
    files = glob.glob("*_cobertura_cds.txt")
    if not files:
        print("No se encontraron archivos '*_cobertura_cds.txt' en este directorio.")
        return

    output_report = "reporte_diagnostico_listeria.tsv"
    print(f"Buscando marcadores específicos en {len(files)} archivos...")
    
    with open(output_report, "w") as out:
        out.write("Muestra\tGene\tLocus_Tag\tCobertura\tCategoria_Marcador\n")
        
        for filepath in sorted(files):
            muestra = os.path.basename(filepath).replace("_cobertura_cds.txt", "")
            hits = process_file(filepath)
            
            for hit in hits:
                out.write(f"{muestra}\t{hit['gene']}\t{hit['locus_tag']}\t{hit['coverage']:.6f}\t{hit['description']}\n")
                
    print(f"¡Listo! El nuevo reporte se guardó en: {output_report}")

if __name__ == "__main__":
    main()
