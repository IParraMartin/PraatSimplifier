import os
import argparse

try:
    import parselmouth
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f'{e}\nInstall the required dependencies. Run requirements.txt')


class PraatSimplifier():
    
    def __init__(self, in_dir: str, out_dir: str):
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.n_timestamps = None
        self.n_formants = None
        self.f_data = []


    def save_to_mono(self):

        """
        Convert all files to mono if necessary.
        """

        for file in os.listdir(self.in_dir):
            if file.endswith('.wav'):
                sound = parselmouth.Sound(os.path.join(self.in_dir, file))
                mono_signal = sound.convert_to_mono()
                output_path = os.path.join(self.out_dir, file)
                mono_signal.save(output_path, format='WAV')
                print(f'Mono sound saved to {output_path}')
        print('Done.')


    def get_formants(self, n_timestamps: int = 10, n_formants: int = 3) -> list:
        
        """
        Extract formants from audio files in the specified directory.

        Parameters:
        n_timestamps (int): The number of timestamps to sample per file.
        n_formants (int): The number of formants to extract.

        Returns:
        list: A list of dictionaries containing formant data.
        """
        
        self.n_timestamps = n_timestamps
        self.n_formants = n_formants
        self.f_data = []

        for file in os.listdir(self.in_dir):
            if file.endswith('.wav'):
                print(f'Analyzing {file}...')
                sound = parselmouth.Sound(os.path.join(self.in_dir, file))
                sound = sound.convert_to_mono()
                dur = sound.get_total_duration()

                time_points = np.linspace(0, dur, self.n_timestamps)

                formant = sound.to_formant_burg(max_number_of_formants=self.n_formants)

                for time in time_points:
                    formant_data = {'sound': file[:-4], 'time': time}
                    for i in range(1, self.n_formants + 1):
                        formant_value = formant.get_value_at_time(i, time)
                        formant_data[f'F{i}'] = round(formant_value, 3) if formant_value is not None else None
                    self.f_data.append(formant_data)
        
        return self.f_data
    

    def export_formants(self):
        
        """
        Export the extracted formant data to a CSV file.
        """
        
        if not self.f_data:
            print("No formant data to export. Run get_formants() first.")
            return
        
        df = pd.DataFrame(self.f_data)
        file_path = f'{self.out_dir}/formants.csv' if self.out_dir else 'formants.csv'
        df.to_csv(file_path, index=False)
        print(f'File saved to {file_path}')


    def plot_formants(self, save_plot: bool = False, dpi: int = 1200):

        """
        Plot the extracted F-values by sound (maximum of 9 for clarity.)
        """

        if not self.f_data:
            print('No formant data. Run get_formants() first.')
            return

        unique_sounds = min(len(set(d['sound'] for d in self.f_data)), 9)
        nrows = np.ceil(unique_sounds / 3).astype(int)
        
        fig, axs = plt.subplots(nrows, 3, figsize=(10, nrows * 3))
        fig.tight_layout(pad=3)

        axs = axs.flatten()

        for ax, (sound, df) in zip(axs, pd.DataFrame(self.f_data).groupby('sound')):
            for i in range(1, self.n_formants + 1):
                ax.plot(df['time'], df[f'F{i}'], label=f'F{i}')
            ax.set_title(sound, fontsize=10)
            ax.set_xlabel('Time (s)', fontsize=10)
            ax.set_ylabel('Frequency (Hz)', fontsize=10)
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            ax.legend(fontsize=8)

        for i in range(unique_sounds, len(axs)):
            axs[i].set_visible(False)

        if save_plot:
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)
            file_path = os.path.join(self.out_dir, 'formant_plots.png')
            try:
                plt.savefig(file_path, dpi=dpi)
                print(f"Plot saved successfully to {file_path}")
            except Exception as e:
                print(f"Failed to save the plot: {e}")

        plt.show()
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simplified code to extract formant values in a .csv file.')
    parser.add_argument('--in_dir', type=str, required=True, help='Directory to your sound files.')
    parser.add_argument('--out_dir', type=str, required=False, default='./', help='Output directory for the .csv file.')
    parser.add_argument('--n_timestamps', type=int, required=False, default=10, help='Number of timestamps to extract the formants from.')
    parser.add_argument('--n_formants', type=int, required=False, default=3, help='Number of formants to extract.')
    parser.add_argument('--save_plot', type=bool, required=False, default=False, help='True = save plot; False = do not save')
    parser.add_argument('--dpi', type=int, required=False, default=1200, help='Quality of plot.')
    parser.add_argument('--save_to_mono', type=bool, required=False, default=False, help='Save to mono all the sounds in the in_dir.')
    args = parser.parse_args()

    simplifier = PraatSimplifier(args.in_dir, args.out_dir)

    formants = simplifier.get_formants(n_formants=args.n_formants, n_timestamps=args.n_timestamps)

    simplifier.export_formants(out_dir=args.out_dir)

    if args.save_plot:
        plot_out_dir = args.out_dir if args.out_dir else './'
        simplifier.plot_formants(plot_out_dir=plot_out_dir, save_plot=True, dpi=args.dpi)

    if args.save_to_mono:
        simplifier.save_to_mono()
    
