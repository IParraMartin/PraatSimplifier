# PraatSimplifier: Parselmouth Based Formant Extractor

<p align="center">
  <img src="resources/logo.png" width="500" title="Logo">
</p>

## 📁 Overview
PraatSimplifier is a Python tool designed to simplify the extraction of formant values from audio files using Praat through the Parselmouth library. This tool allows users to extract formant data from multiple audio files and export the results to a ```.csv``` file for further analysis.

## 🛠️ Features
- Extract Formants: Extract formant values from audio files in a specified directory.
- Flexible Timestamps: Define the timestamps to sample per audio file.
- Customizable Formants: Specify the number of formants to extract.
- CSV Export: Export the extracted formant data to a CSV file for easy analysis.
- Plot Formants: Plot the sound files and export them in a .png image file.
- Mono converter: Save all sounds to mono.
- More features to be released!

## 👨🏽‍💻 Installation
Ensure you have Python installed, and then install the required libraries by running ```requirements.txt``` in the terminal.

```
pip install -r requirements.txt
```

## 🔥 Usage
### Command Line Interface (CLI)
You can use the tool directly from the command line. Below is an example of how to use the CLI:
```
python PraatSimplifier.py \
--sounds_dir=path/to/sound/files \
--out_dir=path/to/output/directory \
--get_formants=True \
--n_timestamps=10 \
--n_formants=3 \
--export_formants_file=True\
--save_plot=True \
--dpi=300 \
--save_to_mono=False
```
Some users may need to use  ```python3``` instead of ```python``` to run the script above. The plotting tool has been limited to a maximum of 9 plots. This was a measure to prevent a lack of visibility of the data in the plots. To make several plots you will have to make independent processes (e.g., for 18 sounds, make 2 files and run the scripts independently).

### Python
Alternatively, you can integrate PraatSimplifier into your Python code:
```
from PraatSimplifier import PraatSimplifier

simplifier = PraatSimplifier(sounds_dir, out_dir)
formant_data = simplifier.get_formants(n_timestamps=100, n_formants=5)
simplifier.export_formants()
```

## 📦 Dependencies
Make sure to install all the dependencies before running the tool.

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.




