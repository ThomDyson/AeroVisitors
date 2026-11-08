
import base64
import csv
import time
from pathlib import Path

from openai import OpenAI
from PIL import Image
from io import BytesIO

# ---------- Configuration ----------
## Your OpenAI API key should be set in the environment variable OPENAI_API_KEY.

MODEL = "gpt-image-2.5-sunburst"
INPUT_CSV = Path("aircraft_redo.csv")
OUTPUT_DIR = Path("aircraft_images")
OUTPUT_DIR.mkdir(exist_ok=True)

client = OpenAI()

PROMPT = """
Draw a highly detailed colored-pencil illustration of the
aircraft type and design: {model}  {description}

Aircraft accuracy:
- Reproduce the recognizable, correct configuration of this specific aircraft type.
- Preserve correct wing layout, engine configuration, tail, landing gear, fuselage proportions and propeller count.
-Ensure the engine and propeller layout is correct.
- Show the complete aircraft, nothing cropped.
- Aircraft is in flight, viewed directly from the side.
- Any propeller or rotor should have a translucent rotational disc with faint blade traces, while keeping the correct number of physical propeller or rotor installations. .
- Realistic colored-pencil artwork, visible pencil strokes, layered colors, fine outlines and subtle crosshatching.
- Isolated aircraft only, centered with margins around it.
- Absolutely no scenery, sky, clouds, runway, airport or hangar.
- No captions, logos, labels, watermarks or other aircraft.
- If the aircraft is a Boeing or Airbus or other commercial airliner, create a subtle representation of a generic airline livery.
- Ensure the livery is applied realistically, following the contours of the aircraft.
- Output on a genuinely transparent background, not a checkerboard pattern, white background or colored backdrop.
- Maintain a true left-facing side elevation. Far-side engines, wheels, wings, and tail surfaces may be naturally hidden or overlap near-side components. Do not move, duplicate, or add components merely to make their total count visible. 
- Fixed landing gear must remain extended in flight. 
- Retractable landing gear must be fully retracted.

Paint scheme: 
 Use a realistic paint scheme appropriate to the exact aircraft type and role. 
 If the aircraft has a strongly associated, commonly used color scheme—such as yellow for a 
 Piper J-3 Cub—prefer that scheme. Otherwise, choose a plausible real-world scheme with 
 restrained variation in the base color and accents. 
 Favor white, cream, silver, natural aluminum, red, burgundy, green, yellow,  or blue as appropriate. 
 Keep military, agricultural, airline, and civilian schemes consistent with the aircraft’s role. 
 Avoid arbitrary fantasy colors. 
 Preserve the pencil-drawing appearance, using subtle colored-pencil accents rather than saturated digital fills.

"""

def generate_image(aircraft_key, aircraft_name):
    output_file = OUTPUT_DIR / f"{aircraft_key}.png"

    if output_file.exists():
        print(f"SKIP: {output_file.name}")
        return True

    prompt = PROMPT.format(model=aircraft_key, description=aircraft_name)

    for attempt in range(1, 4):
        try:
            result = client.images.generate(
                model=MODEL,
                prompt=prompt,
                size="1200x800",
                quality="low",
                background="transparent",
                output_format="png",
            )

            image_bytes = base64.b64decode(
                result.data[0].b64_json
            )

            with Image.open(BytesIO(image_bytes)) as image:
                image = image.convert("RGBA")

                # Resize to exactly 1024 pixels wide.
                #height = round(
                #    image.height * 1024 / image.width
                #)
                #image = image.resize(
                #    (1024, height),
                #    Image.Resampling.LANCZOS,
                #)
                image.save(output_file, format="PNG")

            print(f"OK: {output_file.name}")
            return True

        except Exception as exc:
            print(
                f"ERROR {aircraft_key}, attempt "
                f"{attempt}/3: {exc}"
            )
            if attempt < 3:
                time.sleep(5 * attempt)

    with open(OUTPUT_DIR / "failed.txt", "a",
              encoding="utf-8") as log:
        log.write(f"{aircraft_key},{aircraft_name}\n")

    return False


def main():
    with INPUT_CSV.open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = row["aircraft_key"].strip()
            name = row["aircraft_name"].strip()

            if key and name:
                generate_image(key, name)


if __name__ == "__main__":
    main()
