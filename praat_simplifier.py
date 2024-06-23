import parselmouth
import os
import numpy as np
import pandas as pd
import argparse


try:
    import parselmouth
except ImportError as e:
    print(f'{e}\nParselmouth is required. Try <pip install praat-parselmouth>')


class PraatSimplifier():
    
    def __init__(self):
        self.in_dir = None
        self.n_timestamps = None
        self.n_formants = None
        self.f_data = []

    def get_formants(self, in_dir: str, n_timestamps: int = 10, n_formants: int = 3) -> list:
        
        """
        Extract formants from audio files in the specified directory.

        Parameters:
        in_dir (str): The input directory containing the .wav files.
        n_timestamps (int): The number of timestamps to sample per file.
        n_formants (int): The number of formants to extract.

        Returns:
        list: A list of dictionaries containing formant data.
        """
        
        self.in_dir = in_dir
        self.n_timestamps = n_timestamps
        self.n_formants = n_formants
        self.f_data = []

        for file in os.listdir(self.in_dir):
            if file.endswith('.wav'):
                print(f'Analyzing {file}...')
                sound = parselmouth.Sound(os.path.join(self.in_dir, file))
                sound = sound.convert_to_mono()
                dur = sound.get_total_duration()
                """
                Set the amount of timestamps predefined in the class
                """
                time_points = np.linspace(0, dur, self.n_timestamps)

                formant = sound.to_formant_burg(max_number_of_formants=self.n_formants)

                for time in time_points:
                    """
                    Loop using the amount of formants to extract predefined in
                    n_formants. Delete the last four chars (.wav, .mp3, .mp4)
                    """
                    formant_data = {'sound': file[:-4], 'time': time}
                    for i in range(1, self.n_formants + 1):
                        formant_value = formant.get_value_at_time(i, time)
                        formant_data[f'F{i}'] = round(formant_value, 3) if formant_value is not None else None
                    self.f_data.append(formant_data)

        return self.f_data
    
    def export_formants(self, out_dir: str = None):
        
        """
        Export the extracted formant data to a CSV file.

        Parameters:
        out_dir (str): The output directory for the CSV file. Defaults to the current directory.
        """
        
        if not self.f_data:
            print("No formant data to export. Run get_formants() first.")
            return
        
        df = pd.DataFrame(self.f_data)
        file_path = f'{out_dir}/formants.csv' if out_dir else 'formants.csv'
        df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplified code to extract formant values in a .csv file.')
    parser.add_argument('--sounds_dir', type=str, required=True, help='Directory to your sound files.')
    parser.add_argument('--n_timestamps', type=int, required=True, help='Number of timestamps to extract the formants from.')
    parser.add_argument('--n_formants', type=int, required=True, help='Number of formants to extract.')
    parser.add_argument('--out_dir', type=str, required=True, help='Output directory for the .csv file.')
    args = parser.parse_args()

    simplifier = PraatSimplifier()

    formants = simplifier.get_formants(
        in_dir=args.sounds_dir,
        n_formants=args.n_formants,
        n_timestamps=args.n_timestamps
    )
    
    simplifier.export_formants(out_dir=args.out_dir)