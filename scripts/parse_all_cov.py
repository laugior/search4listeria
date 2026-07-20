#!/usr/bin/env python3
import os
import glob
import re


def parse_gtf_attributes(attributes_str):
    """Extrae un diccionario con los atributos clave del GTF."""
    return dict(re.findall(r'(\w+)\s+"([^"]*)"', attributes_str))


def process_file(filepath):
    results = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue

            parts = line.rstrip('\n').split('\t')
            if len(parts) < 9:
                continue

            # Analizamos nivel CDS para evitar duplicaciones
            if parts[2] != "CDS":
                continue

            try:
                coverage = float(parts[-1])
            except ValueError:
                continue

            # Único filtro: cobertura estrictamente mayor a 0
            if coverage <= 0.0:
                continue

            attributes = parse_gtf_attributes(parts[8])
            results.append({
                "gene": attributes.get("gene", ""),
                "locus_tag": attributes.get("locus_tag", ""),
                "product": attributes.get("product", ""),
                "coverage": coverage,
            })
    return results


def main():
    files = glob.glob("*_cobertura_cds.txt")
    if not files:
        print("No se encontraron archivos '*_cobertura_cds.txt' en este directorio.")
        return

    output_report = "reporte_cobertura.tsv"
    print(f"Procesando {len(files)} archivos...")

    total = 0
    with open(output_report, "w") as out:
        out.write("Muestra\tGene\tLocus_Tag\tProducto\tCobertura\n")
        for filepath in sorted(files):
            muestra = os.path.basename(filepath).replace("_cobertura_cds.txt", "")
            hits = process_file(filepath)
            total += len(hits)
            # Orden descendente por cobertura dentro de cada muestra
            for hit in sorted(hits, key=lambda h: h["coverage"], reverse=True):
                out.write(
                    f"{muestra}\t{hit['gene']}\t{hit['locus_tag']}\t"
                    f"{hit['product']}\t{hit['coverage']:.6f}\n"
                )

    print(f"¡Listo! {total} CDS con cobertura > 0 guardados en: {output_report}")


if __name__ == "__main__":
    main()
