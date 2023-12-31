import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Setting the style
plt.style.use('science')

remap_datasets = {
    'cora': 'Cora',
    'citeseer': 'Citeseer',
    'pubmed': 'Pubmed',
    'reddit': 'Reddit',
    'flickr': 'Flickr',
    'yelp': 'Yelp',
    'arxiv': 'ogbn-arxiv',
    'ogb-arxiv': 'ogbn-arxiv',
    'ogbn-arxiv': 'ogbn-arxiv',
    'products': 'ogbn-products',
    'ogb-products': 'ogbn-products',
    'ogbn-products': 'ogbn-products',
}

def plot_single_dataset(dataset_name, datasets_info, entropy_plots_dir):
    dataset_dir = os.path.join(entropy_plots_dir, dataset_name)

    # Define the paths to the CSV files for the current dataset
    csv_mean_0_path = os.path.join(dataset_dir, 'mean_entropy0.csv')
    csv_mean_1_path = os.path.join(dataset_dir, 'mean_entropy1.csv')
    csv_std_0_path = os.path.join(dataset_dir, 'std_entropy0.csv')
    csv_std_1_path = os.path.join(dataset_dir, 'std_entropy1.csv')

    # Check if the CSV files exist for the current dataset
    if os.path.exists(csv_mean_0_path) and os.path.exists(csv_mean_1_path) and os.path.exists(
            csv_std_0_path) and os.path.exists(csv_std_1_path):
        # Update the steps_per_epoch_corrected calculation to use the epoch count from the dictionary
        overall_max_step = max(pd.read_csv(csv_mean_0_path)['Step'].max(), pd.read_csv(csv_mean_1_path)['Step'].max())
        steps_per_epoch_corrected = overall_max_step / datasets_info[dataset_name]['epochs']

        # Setting up subplots
        fig, ax = plt.subplots(1, 2, figsize=(24, 8))

        # Call the process_and_plot function to generate the plot for the dataset
        process_and_plot(csv_mean_0_path, csv_mean_1_path, csv_std_0_path, csv_std_1_path, steps_per_epoch_corrected,
                         datasets_info[dataset_name]['xlim'], ax, dataset_name)

        # Save the figure for the given dataset
        output_path = os.path.join(entropy_plots_dir, f"{dataset_name}-entropy-plot-single.pdf")
        plt.tight_layout()
        plt.savefig(output_path, format='pdf')
        plt.show()


def process_and_plot(csv_mean_0, csv_mean_1, csv_std_0, csv_std_1, steps_per_epoch_corrected, xlim_value, ax,
                     dataset_name):

    # Load mean entropy CSV files
    df = pd.read_csv(csv_mean_0)
    df_new = pd.read_csv(csv_mean_1)

    # Extract column names for mean entropy
    mean_entropy_0_col = df.columns[1]
    mean_entropy_1_col = df_new.columns[1]

    # Convert the 'Step' column to 'Epoch' for mean entropy data
    df['Epoch'] = np.ceil(df['Step'] / steps_per_epoch_corrected).astype(int)
    df_new['Epoch'] = np.ceil(df_new['Step'] / steps_per_epoch_corrected).astype(int)

    # Compute the average mean entropy for each epoch in both datasets
    avg_entropy_df = df.groupby('Epoch')[mean_entropy_0_col].mean().reset_index()
    avg_entropy_df_new = df_new.groupby('Epoch')[mean_entropy_1_col].mean().reset_index()

    # Merge the average mean entropies from both datasets
    avg_entropy_combined = pd.merge(avg_entropy_df, avg_entropy_df_new, on='Epoch', how='outer')

    # Load standard deviation CSV files
    df_std = pd.read_csv(csv_std_0)
    df_std_new = pd.read_csv(csv_std_1)

    # Extract column names for standard deviation
    std_entropy_0_col = df_std.columns[1]
    std_entropy_1_col = df_std_new.columns[1]

    # Convert the 'Step' column to 'Epoch' for standard deviation data
    df_std['Epoch'] = np.ceil(df_std['Step'] / steps_per_epoch_corrected).astype(int)
    df_std_new['Epoch'] = np.ceil(df_std_new['Step'] / steps_per_epoch_corrected).astype(int)

    # Compute the average standard deviation for each epoch in both datasets
    avg_std_df = df_std.groupby('Epoch')[std_entropy_0_col].mean().reset_index()
    avg_std_df_new = df_std_new.groupby('Epoch')[std_entropy_1_col].mean().reset_index()

    # Merge the average standard deviations from both datasets
    avg_std_combined = pd.merge(avg_std_df, avg_std_df_new, on='Epoch', how='outer')

    # Determine y-limits based on the data
    mean_entropy_ymin = min(avg_entropy_combined[mean_entropy_0_col].min(),
                            avg_entropy_combined[mean_entropy_1_col].min()) - 0.05
    mean_entropy_ymax = max(avg_entropy_combined[mean_entropy_0_col].max(),
                            avg_entropy_combined[mean_entropy_1_col].max()) + 0.05

    std_entropy_ymin = min(avg_std_combined[std_entropy_0_col].min(), avg_std_combined[std_entropy_1_col].min()) - 0.005
    std_entropy_ymax = max(avg_std_combined[std_entropy_0_col].max(), avg_std_combined[std_entropy_1_col].max()) + 0.005

    # Plotting mean entropy on the left subplot
    ax[0].plot(avg_entropy_combined['Epoch'], avg_entropy_combined[mean_entropy_0_col],
               label='1-hop node sampling', color='#4040FF', linewidth=4.0, linestyle='--')
    ax[0].plot(avg_entropy_combined['Epoch'], avg_entropy_combined[mean_entropy_1_col],
               label='2-hop node sampling', color='#4040FF', linewidth=4.0, linestyle='solid')
    ax[0].set_xlabel('Epoch', fontsize=30)
    ax[0].set_ylabel('Mean Entropy', fontsize=30)
    ax[0].set_xticks(ticks=range(0, xlim_value + 1, xlim_value // 10))
    ax[0].tick_params(axis='both', which='major', labelsize=20)
    ax[0].set_ylim(mean_entropy_ymin, mean_entropy_ymax)
    ax[0].set_xlim(0, xlim_value)
    ax[0].legend(fontsize=30)
    ax[0].grid(True)
    ax[0].set_title(remap_datasets[dataset_name.lower()], fontsize=40)

    # Plotting standard deviation on the right subplot
    ax[1].plot(avg_std_combined['Epoch'], avg_std_combined[std_entropy_0_col],
               label='1-hop node sampling', color='#4040FF', linewidth=4.0, linestyle='--')
    ax[1].plot(avg_std_combined['Epoch'], avg_std_combined[std_entropy_1_col],
               label='2-hop node sampling', color='#4040FF', linewidth=4.0, linestyle='solid')
    ax[1].set_xlabel('Epoch', fontsize=30)
    ax[1].set_ylabel('Entropy Standard Deviation', fontsize=30)
    ax[1].set_xticks(ticks=range(0, xlim_value + 1, xlim_value // 10))
    ax[1].tick_params(axis='both', which='major', labelsize=20)
    ax[1].set_ylim(std_entropy_ymin, std_entropy_ymax)
    ax[1].set_xlim(0, xlim_value)
    ax[1].legend(fontsize=30)
    ax[1].grid(True)
    ax[1].set_title(remap_datasets[dataset_name.lower()], fontsize=40)


def plot_on_subplot(csv_mean_0, csv_mean_1, csv_std_0, csv_std_1, steps_per_epoch_corrected, xlim_value, ax,
                    dataset_name):
    # Call the process_and_plot function with the provided subplot axes
    process_and_plot(csv_mean_0, csv_mean_1, csv_std_0, csv_std_1, steps_per_epoch_corrected, xlim_value, ax,
                     dataset_name)


def generate_combined_plot(datasets_info, entropy_plots_dir):
    # Order in which datasets should be plotted
    ordered_datasets = ['Cora', 'Citeseer', 'Pubmed', 'Reddit', 'Flickr', 'Yelp', 'ogbn-arxiv', 'ogbn-products']

    # Number of datasets
    num_datasets = len(ordered_datasets)

    # Calculate the number of figures required
    num_figures = (num_datasets + 3) // 4  # Each figure can accommodate 4 datasets (8 plots)

    for fig_num in range(num_figures):
        # Start and end indices for slicing dataset names for the current figure
        start_idx = fig_num * 4
        end_idx = min((fig_num + 1) * 4, num_datasets)

        # Create a subplot grid with a maximum of 4 rows and 2 columns for the current figure
        fig, axs = plt.subplots(min(4, end_idx - start_idx), 2, figsize=(24, 8 * min(4, end_idx - start_idx)))

        for idx, dataset_name in enumerate(ordered_datasets[start_idx:end_idx]):
            dataset_info = datasets_info[dataset_name]
            dataset_dir = os.path.join(entropy_plots_dir, dataset_name)

            # Define the paths to the CSV files for the current dataset
            csv_mean_0_path = os.path.join(dataset_dir, 'mean_entropy0.csv')
            csv_mean_1_path = os.path.join(dataset_dir, 'mean_entropy1.csv')
            csv_std_0_path = os.path.join(dataset_dir, 'std_entropy0.csv')
            csv_std_1_path = os.path.join(dataset_dir, 'std_entropy1.csv')

            # Check if the CSV files exist for the current dataset
            if os.path.exists(csv_mean_0_path) and os.path.exists(csv_mean_1_path) and os.path.exists(
                    csv_std_0_path) and os.path.exists(csv_std_1_path):
                # Update the steps_per_epoch_corrected calculation to use the epoch count from the dictionary
                overall_max_step = max(pd.read_csv(csv_mean_0_path)['Step'].max(),
                                       pd.read_csv(csv_mean_1_path)['Step'].max())
                steps_per_epoch_corrected = overall_max_step / dataset_info['epochs']

                # Generate the plot for the current dataset on the corresponding subplot
                plot_on_subplot(csv_mean_0_path, csv_mean_1_path, csv_std_0_path, csv_std_1_path,
                                steps_per_epoch_corrected, dataset_info['xlim'], axs[idx], dataset_name)

        # Save the combined figure for the current set of datasets
        output_path = os.path.join(entropy_plots_dir, f"combined-entropy-plot-{fig_num + 1}.pdf")
        plt.tight_layout()
        plt.savefig(output_path, format='pdf')
        plt.show()

# Dictionary with the number of epochs and x-limits for each dataset
datasets_info = {
    'Citeseer': {'epochs': 300, 'xlim': 50},
    'Cora': {'epochs': 50, 'xlim': 50},
    'Flickr': {'epochs': 300, 'xlim': 100},
    'ogbn-arxiv': {'epochs': 150, 'xlim': 150},
    'ogbn-products': {'epochs': 100, 'xlim': 100},
    'Pubmed': {'epochs': 300, 'xlim': 100},
    'Reddit': {'epochs': 50, 'xlim': 50},
    'Yelp': {'epochs': 150, 'xlim': 100}
}

# Define the path to the 'entropy_plots' directory
entropy_plots_dir = './entropy_plots'

# Call the new function to generate the combined plot
generate_combined_plot(datasets_info, entropy_plots_dir)

plot_single_dataset('ogbn-arxiv', datasets_info, entropy_plots_dir)
