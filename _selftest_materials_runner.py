from pathlib import Path
from time import perf_counter

from backend.app.services.renderer import renderer

base = Path("backend/data")
input_img = base / "inputs" / "d34b7c4e-90b0-4638-892b-f6d026f9e26c.png"
materials_root = Path("Materiales/arauco")
mat_enebro = materials_root / "Enebro.jpg"
mat_jerez = materials_root / "Jerez.png"
out_dir = base / "outputs"
out_dir.mkdir(parents=True, exist_ok=True)

if not input_img.exists():
    raise FileNotFoundError(f"Missing test input: {input_img}")

cases = [
    ("mix_one", "mix", [str(mat_enebro)], ""),
    ("mix_two", "mix", [str(mat_enebro), str(mat_jerez)], ""),
    ("zones_one", "zones", [str(mat_enebro)], "Aplica enebro solo en maderas y muebles de carpinteria; no tocar vidrio, metal ni piso."),
    ("zones_two", "zones", [str(mat_enebro), str(mat_jerez)], "Enebro en enchape superior y frentes de madera oscuros; Jerez en modulos claros laterales; no tocar vidrio, acero ni piso."),
]

for name, mode, mats, plan in cases:
    out = out_dir / f"selftest-{name}.png"
    start = perf_counter()
    meta = renderer.generate_material_edit(
        input_image_path=str(input_img),
        material_paths=mats,
        output_image_path=str(out),
        prompt="Fotografia arquitectonica interior, ultra realista, luz natural de dia.",
        material_mode=mode,
        material_plan=plan,
        quality="balanced",
        seed=42,
    )
    took = perf_counter() - start
    print(name, out.name, f"elapsed={took:.2f}s", meta)
