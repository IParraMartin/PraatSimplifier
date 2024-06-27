import os
import argparse

try:
    import parselmouth
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f'{e}. Install the required dependencies. Try: <pip install -r requirements.txt>')


class PraatSimplifier():
    
    def __init__(self, in_dir: str, out_dir: str):
        self.in_dir = in_dir
        self.out_dir = out_dir


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

    
    def plot_sound_amplitude(self, sound_dir: str, start_time: float = None, end_time: float = None, save_amplitude_plot: bool = False):

        """
        Plots the sound amplitude of a sound file.

        Parameters:
            - sound_dir: directory to the selected sound
            - start_time: start at time x (float)
            - end_time: trim at time y (float)

        Returns: An amplitude plot of the sound.
        """

        assert sound_dir.endswith('.wav'), 'plot_sound_amplitude() can only process one .wav sound file.'

        try:
            sound = parselmouth.Sound(sound_dir)
            if start_time is not None and end_time is not None:
                extracted_sound = sound.extract_part(from_time=start_time, to_time=end_time, preserve_times=True)
            else:
                extracted_sound = sound
            extracted_sound = extracted_sound.convert_to_mono()

            plt.figure(figsize=(10, 5))
            plt.plot(extracted_sound.xs(), extracted_sound.values[0], linewidth=0.3, color='rebeccapurple')
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            plt.title('Sound Wave')
            plt.grid(True, alpha=0.5)

            if save_amplitude_plot:
                assert self.out_dir, 'Specify --out_dir to save the plot.'
                if not os.path.exists(self.out_dir):
                    os.makedirs(self.out_dir)
                plt.savefig(os.path.join(self.out_dir, 'amplitude_plot.png'), dpi=1200)
            
            plt.show()
        except Exception as e:
            print(f'An error occurred: {e}')


    def plot_formants(self, save_formant_plot: bool = False, dpi: int = 1200):

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

        if save_formant_plot:
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
    """
    Args for formant analysis
    """
    parser.add_argument('--in_dir', type=str, required=False, help='Directory to your sound files.')
    parser.add_argument('--out_dir', type=str, required=False, default='./', help='Output directory for the .csv file.')
    parser.add_argument('--get_formants', type=bool, required=False, default=False, help='Analyze formants.')
    parser.add_argument('--n_timestamps', type=int, required=False, default=10, help='Number of timestamps to extract the formants from.')
    parser.add_argument('--n_formants', type=int, required=False, default=3, help='Number of formants to extract.')
    parser.add_argument('--export_formants_file', type=bool, required=False, default=False, help='Export .csv with formants.')
    parser.add_argument('--save_formant_plot', type=bool, required=False, default=False, help='True = save plot; False = do not save')
    parser.add_argument('--dpi', type=int, required=False, default=300, help='Quality of plot.')
    """
    Args for audio transformantion
    """
    parser.add_argument('--save_to_mono', type=bool, required=False, default=False, help='Save to mono all the sounds in the in_dir.')
    """
    Args for sound amplitude ploting.
    """
    parser.add_argument('--plot_sound_amplitude', type=bool, required=False, default=False, help='Plot a sound amplitude.')
    parser.add_argument('--sound_dir', type=str, required=False, help='Path to the sound file for plotting amplitude.')
    parser.add_argument('--start_time', type=float, required=False, help='Start time to plot.')
    parser.add_argument('--end_time', type=float, required=False, help='End time to plot.')
    parser.add_argument('--save_amplitude_plot', type=bool, required=False, default=False, help='Save amplitude plot.')

    args = parser.parse_args()
 
    simplifier = PraatSimplifier(args.in_dir, args.out_dir)

    if args.get_formants:
        formants = simplifier.get_formants(n_formants=args.n_formants, n_timestamps=args.n_timestamps)

    if args.export_formants_file:
        simplifier.export_formants()

    if args.save_formant_plot:
        simplifier.plot_formants(save_formant_plot=True, dpi=args.dpi)

    if args.save_to_mono:
        simplifier.save_to_mono()

    if args.plot_sound_amplitude:
        simplifier.plot_sound_amplitude(args.sound_dir, args.start_time, args.end_time, args.save_amplitude_plot)
