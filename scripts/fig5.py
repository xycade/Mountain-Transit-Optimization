import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D

# Set global font to Times New Roman (Academic Journal Standard)
plt.rcParams['font.sans-serif'] = ['Times New Roman']
plt.rcParams['axes.unicode_minus'] = False


def plot_3d_pareto_with_scenarios(csv_path):
    # 1. Load NSGA-II Results
    df = pd.read_csv(csv_path)

    f1 = df['F1_AvgTime']
    f2 = df['F2_Cost']
    f3 = df['F3_Overlap_Ratio']

    # 2. Extract the 4 specific scenarios using mathematical logic
    idx_sp = f1.idxmin()  # Minimizes F1
    idx_ca = f2.idxmin()  # Minimizes F2
    idx_hs = f3.idxmin()  # Minimizes F3

    # Calculate Balanced (BD) Knee-point via min normalized distance to origin
    norm_f1 = (f1 - f1.min()) / (f1.max() - f1.min())
    norm_f2 = (f2 - f2.min()) / (f2.max() - f2.min())
    norm_f3 = (f3 - f3.min()) / (f3.max() - f3.min())
    distances = np.sqrt(norm_f1 ** 2 + norm_f2 ** 2 + norm_f3 ** 2)
    idx_bd = distances.idxmin()

    # Create a dictionary to easily loop through scenarios for plotting
    scenarios = {
        'SP': idx_sp,
        'CA': idx_ca,
        'HS': idx_hs,
        'BD': idx_bd
    }

    # 3. Create 3D Canvas
    fig = plt.figure(figsize=(10, 8), dpi=500)
    ax = fig.add_subplot(111, projection='3d')

    # 4. Plot the background Pareto Front
    scatter = ax.scatter(f1, f2, f3, c=f3, cmap='viridis', s=70, alpha=0.5, edgecolors='w', linewidth=0.5)

    # 5. Highlight the 4 Scenarios
    for name, idx in scenarios.items():
        # Plot a large red star for the scenario point
        ax.scatter(f1[idx], f2[idx], f3[idx],
                   color='red', marker='*', s=250, edgecolor='black', linewidth=0.8, alpha=1.0, zorder=5)

        # Add Text Annotation
        ax.text(f1[idx], f2[idx], f3[idx] + 0.001,  # Slight Z offset so text doesn't overlap marker
                f' {name}', color='darkred', fontsize=12, fontweight='bold', zorder=6)

    # 6. Axis Labels (Clean English annotations)
    ax.set_xlabel('F1 (Efficiency: Avg Travel Time / min)', fontsize=12, labelpad=10)
    ax.set_ylabel('F2 (Operator Cost: CNY/h)', fontsize=12, labelpad=10)
    ax.set_zlabel('F3 (Service: Rail Overlap Ratio)', fontsize=12, labelpad=10)

    ax.tick_params(axis='both', which='major', labelsize=10)

    # 7. Adjust view angle
    ax.view_init(elev=25, azim=-50)

    # 8. Colorbar
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('F3: Rail Overlap Ratio', fontsize=11)

    # 9. Save output to results folder
    plt.tight_layout()
    save_path = os.path.join('results', 'Figure_5_3D_Pareto_Front.png')
    plt.savefig(save_path, format='png', bbox_inches='tight')
    print(f"Annotated 3D Pareto plot successfully saved to: {save_path}")


if __name__ == '__main__':
    # Using relative path for portability
    target_csv = 'results/Pareto_Front_Solutions.csv'
    plot_3d_pareto_with_scenarios(target_csv)