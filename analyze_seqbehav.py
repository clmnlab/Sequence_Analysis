import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class mySubj:
    def __init__(self, file_path):
        """
        Initialize the class and load data from the specified file.
        """
        self.data = None
        self.load_data_from_file(file_path)

    def load_data_from_file(self, file_path):
        """
        Load data from a given file path.
        """
        try:
            self.data = pd.read_csv(file_path, sep='\t', engine='python')
            print("Data loaded successfully.")
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")

    def calculate_rt_mt(self):
        """
        Calculate the average RT and MT for each Horizon and seqType.
        """
        if self.data is None:
            print("Data not loaded. Please load the data first.")
            return
        
        data_no_error = self.data[self.data['isError'] == 0]
        self.rt_analysis = data_no_error.groupby(['seqType', 'Horizon'])['RT'].mean().reset_index()
        self.mt_analysis = data_no_error.groupby(['seqType', 'Horizon'])['MT'].mean().reset_index()

    def calculate_error_proportion(self):
        """
        Calculate the proportion of trials with isError=0 for each Horizon and seqType.
        """
        if self.data is None:
            print("Data not loaded. Please load the data first.")
            return

        total_trials = self.data.groupby(['seqType', 'Horizon']).size().reset_index(name='TotalCount')
        n_error_trials = self.data[self.data['isError'] == 1].groupby(['seqType', 'Horizon']).size().reset_index(name='ErrorCount')
        n_correct_trials = self.data[self.data['isError'] == 0].groupby(['seqType', 'Horizon']).size().reset_index(name='CorrectCount')

        self.error_proportion = total_trials.merge(n_error_trials, on=['seqType', 'Horizon'])
        self.error_proportion['ErrorRate'] = self.error_proportion['ErrorCount'] / self.error_proportion['TotalCount']


    def calculate_ipi(self):
        """Calculate the Inter-Press Interval (IPI) for pressTime data."""
        if self.data is None:
            print("Data not loaded. Please load the data first.")
            return

        # Correctly calculate IPI by subtracting adjacent pressTime columns
        for i in range(13):
            self.data[f'IPI{i+1}'] = self.data[f'pressTime{i+1}'] - self.data[f'pressTime{i}']

        # Assuming seqType and Horizon are already part of self.data
        self.ipi_data = self.data[['seqType', 'Horizon'] + [f'IPI{i+1}' for i in range(13)]]


    def visualize_ipi(self):
        """Visualize the IPI results for each Horizon and SeqType with SEM."""
        if self.data is None:
            print("Data not loaded. Please load the data first.")
            return
        if self.ipi_data is None:
            print("IPI data not calculated. Please calculate IPI first.")
            return

        # Define a red color gradient
        horizons = sorted(self.data['Horizon'].unique())
        colors = plt.cm.Reds(np.linspace(0.3, 1, len(horizons)))

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey=True)

        # In the visualize_ipi method
        for seq_type in [1, 2]:
            title = "Spatial" if seq_type == 1 else "Numbers"
            ax = axes[seq_type - 1]
            for horizon, color in zip(horizons, colors):
                subset = self.data[(self.data['seqType'] == seq_type) & (self.data['Horizon'] == horizon)]
                ipi_means = subset[[f'IPI{i + 1}' for i in range(13)]].mean()
                ipi_sems = subset[[f'IPI{i + 1}' for i in range(13)]].sem()
                ax.errorbar(range(1, 14), ipi_means, yerr=ipi_sems, marker='o', color=color, label=f'Horizon {horizon}')

            ax.set_title(title, fontsize=20)
            ax.set_xlabel('IPI Number', fontsize=14)
            ax.set_ylabel('Average IPI (with SEM)', fontsize=14)
            ax.tick_params(axis='both', which='major', labelsize=12)
            ax.legend(loc='best')
            ax.grid(True)

        plt.suptitle('Inter-Press Interval (IPI) by Horizon and SeqType', fontsize=16)
        plt.tight_layout()
        plt.show()


    def visualize_rt_mt(self):
        """
        Visualize the calculated RT, MT, and error rates with SEM.
        """
        if self.data is None:
            print("Data not loaded. Please load the data first.")
            return

        # Filter out trials with errors
        data_no_error = self.data[self.data['isError'] == 0]

        # Calculate SEM for RT and MT
        rt_sem = data_no_error.groupby(['seqType', 'Horizon'])['RT'].sem().reset_index()
        mt_sem = data_no_error.groupby(['seqType', 'Horizon'])['MT'].sem().reset_index()

        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))  # Adjust for three plots
    # In the visualize_results method

        # Plotting RT with SEM
        for seq_type in self.rt_analysis['seqType'].unique():
            label = "Spatial" if seq_type == 1 else "Numbers"
            subset_rt = self.rt_analysis[self.rt_analysis['seqType'] == seq_type]
            subset_sem_rt = rt_sem[rt_sem['seqType'] == seq_type]
            axes[0].errorbar(subset_rt['Horizon'], subset_rt['RT'], yerr=subset_sem_rt['RT'], marker='o', label=label)
        
        axes[0].set_title('Average RT by Horizon and seqType with SEM',fontsize=15)
        axes[0].set_xlabel('Horizon',fontsize=14)
        axes[0].set_ylabel('Average RT',fontsize=14)
        axes[0].tick_params(axis='both', which='major', labelsize=12)

        axes[0].legend()
        axes[0].grid(True)

        # Plotting MT with SEM
        for seq_type in self.mt_analysis['seqType'].unique():
            label = "Spatial" if seq_type == 1 else "Numbers"
            subset_mt = self.mt_analysis[self.mt_analysis['seqType'] == seq_type]
            subset_sem_mt = mt_sem[mt_sem['seqType'] == seq_type]
            axes[1].errorbar(subset_mt['Horizon'], subset_mt['MT'], yerr=subset_sem_mt['MT'], marker='o', label=label)
        
        axes[1].set_title('Average MT by Horizon and seqType with SEM',fontsize=15)
        axes[1].set_xlabel('Horizon',fontsize=14)
        axes[1].set_ylabel('Average MT',fontsize=14)
        axes[1].tick_params(axis='both', which='major', labelsize=12)

        axes[1].legend()
        axes[1].grid(True)

        # Plotting Error Rate
        for seq_type in self.error_proportion['seqType'].unique():
            label = "Spatial" if seq_type == 1 else "Numbers"
            subset_error = self.error_proportion[self.error_proportion['seqType'] == seq_type]
            axes[2].plot(subset_error['Horizon'], subset_error['ErrorRate'], marker='o', label=label)
        
        axes[2].set_title('Error Rate by Horizon and seqType',fontsize=15)
        axes[2].set_xlabel('Horizon',fontsize=14)
        axes[2].set_ylabel('Error Rate',fontsize=14)
        axes[2].tick_params(axis='both', which='major', labelsize=12)

        axes[2].legend()
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()
