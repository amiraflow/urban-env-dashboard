"""
Model Visualizations for Part 1: Model Stage (10 points)

Creates clean, professional visualizations for the clustering analysis:
1. Elbow Plot - K selection justification
2. PCA Scatter Plot - Cities colored by cluster, Vienna highlighted
3. Box Plots - Comparing indicators across clusters

Style: Minimal, high data-ink ratio, ColorBrewer-inspired palettes
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.clustering import load_city_data, prepare_clustering_features, find_optimal_clusters, perform_clustering

# =============================================================================
# STYLE CONFIGURATION
# =============================================================================
# ColorBrewer "Dark2" qualitative palette - colorblind-friendly
# Matches the dashboard colors for consistency
COLORS = {
    'primary': '#2E5C8A',
    'accent': '#D95F02',  # Orange for Vienna (colorblind-safe)
    'cluster_0': '#1B9E77',  # Teal - Clean & Green
    'cluster_1': '#7570B3',  # Purple - Moderate Urban
    'cluster_2': '#E7298A',  # Magenta - High Density
    'cluster_3': '#66A61E',  # Green - Industrial/Polluted
    'text': '#333333',
    'grid': '#EEEEEE',
    'background': '#FFFFFF',
}

CLUSTER_COLORS = [COLORS['cluster_0'], COLORS['cluster_1'],
                  COLORS['cluster_2'], COLORS['cluster_3']]

# Set matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'legend.frameon': True,
    'legend.framealpha': 0.9,
})


def create_elbow_plot(cluster_analysis, save_path=None):
    """
    Create elbow plot showing inertia and silhouette scores.
    Justifies the selection of K=4 clusters.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    K_range = cluster_analysis['K_range']
    inertias = cluster_analysis['inertias']
    silhouettes = cluster_analysis['silhouette_scores']

    # Plot 1: Elbow Method (Inertia)
    ax1.plot(K_range, inertias, 'o-', color=COLORS['primary'], linewidth=2, markersize=8)
    ax1.axvline(x=4, color=COLORS['accent'], linestyle='--', linewidth=2, alpha=0.8,
                label='Selected K=4')
    ax1.set_xlabel('Number of Clusters (K)')
    ax1.set_ylabel('Inertia (Within-cluster Sum of Squares)')
    ax1.set_title('Elbow Method for Optimal K')
    ax1.set_xticks(K_range)
    ax1.legend(loc='upper right')

    # Add annotation
    ax1.annotate('Elbow point', xy=(4, inertias[2]), xytext=(5.5, inertias[2] + 20),
                 fontsize=10, arrowprops=dict(arrowstyle='->', color=COLORS['text']),
                 color=COLORS['text'])

    # Plot 2: Silhouette Score
    ax2.plot(K_range, silhouettes, 's-', color=COLORS['primary'], linewidth=2, markersize=8)
    ax2.axvline(x=4, color=COLORS['accent'], linestyle='--', linewidth=2, alpha=0.8,
                label='Selected K=4')
    ax2.set_xlabel('Number of Clusters (K)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis')
    ax2.set_xticks(K_range)
    ax2.legend(loc='upper right')

    # Highlight K=4 point
    k4_idx = K_range.index(4)
    ax2.scatter([4], [silhouettes[k4_idx]], s=150, color=COLORS['accent'], zorder=5,
                edgecolor='white', linewidth=2)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Elbow plot saved to: {save_path}")

    return fig


def create_pca_scatter_plot(df_clustered, cluster_info, save_path=None):
    """
    Create 2D PCA scatter plot with cities colored by cluster.
    Vienna highlighted with a star marker.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot each cluster
    for i, info in enumerate(cluster_info):
        cluster_data = df_clustered[df_clustered['cluster'] == i]
        # Exclude Vienna for separate plotting
        cluster_data_no_vienna = cluster_data[cluster_data['city'] != 'Vienna']

        ax.scatter(cluster_data_no_vienna['pca_1'], cluster_data_no_vienna['pca_2'],
                   c=CLUSTER_COLORS[i], s=80, alpha=0.7,
                   label=f"Cluster {i}: {info['name']} ({info['n_cities']} cities)",
                   edgecolor='white', linewidth=0.5)

    # Plot Vienna with special marker
    vienna = df_clustered[df_clustered['city'] == 'Vienna'].iloc[0]
    ax.scatter(vienna['pca_1'], vienna['pca_2'],
               marker='*', s=400, c=COLORS['accent'],
               edgecolor='black', linewidth=1.5, zorder=10,
               label='Vienna')

    # Add Vienna label
    ax.annotate('Vienna', (vienna['pca_1'], vienna['pca_2']),
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, fontweight='bold', color=COLORS['accent'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Add some other city labels for context
    notable_cities = ['Tokyo', 'Delhi', 'Sydney', 'New York', 'London', 'Beijing']
    for city in notable_cities:
        city_row = df_clustered[df_clustered['city'] == city]
        if len(city_row) > 0:
            city_row = city_row.iloc[0]
            ax.annotate(city, (city_row['pca_1'], city_row['pca_2']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, alpha=0.8)

    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.set_title('Cities Clustered by Environmental Characteristics\n(PCA Visualization)')

    # Legend outside plot
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=True)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"PCA scatter plot saved to: {save_path}")

    return fig


def create_cluster_boxplots(df_clustered, cluster_info, save_path=None):
    """
    Create box plots comparing key indicators across clusters.
    Includes Vienna's position marked on its cluster.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    indicators = [
        ('pm25', 'PM2.5 (μg/m³)', axes[0, 0]),
        ('green_space_pct', 'Green Space (%)', axes[0, 1]),
        ('population_density', 'Population Density (per km²)', axes[1, 0]),
        ('traffic_intensity', 'Traffic Intensity (vehicles/day/1000 people)', axes[1, 1]),
    ]

    # Get Vienna data
    vienna = df_clustered[df_clustered['city'] == 'Vienna'].iloc[0]

    for col, title, ax in indicators:
        # Create box plot
        bp = ax.boxplot([df_clustered[df_clustered['cluster'] == i][col].values
                         for i in range(4)],
                        patch_artist=True, positions=[0, 1, 2, 3])

        # Color boxes
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(CLUSTER_COLORS[i])
            patch.set_alpha(0.7)

        # Style whiskers and caps
        for element in ['whiskers', 'caps', 'medians']:
            for line in bp[element]:
                line.set_color(COLORS['text'])
                line.set_linewidth(1.5)

        # Mark Vienna's position
        vienna_cluster = int(vienna['cluster'])
        vienna_value = vienna[col]
        ax.scatter(vienna_cluster, vienna_value, marker='*', s=200,
                   color=COLORS['accent'], edgecolor='black', linewidth=1,
                   zorder=10, label='Vienna')

        ax.set_title(title)
        ax.set_xlabel('Cluster')
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels([f"{i}\n{cluster_info[i]['name'][:10]}" for i in range(4)],
                           fontsize=9)

        # Add legend only to first plot
        if col == 'pm25':
            ax.legend(loc='upper right')

    plt.suptitle('Environmental Indicators by Cluster', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Box plots saved to: {save_path}")

    return fig


def create_cluster_profile_radar(df_clustered, cluster_info, save_path=None):
    """
    Create a radar/spider chart showing cluster profiles.
    Optional visualization for extra insight.
    """
    # Normalize features for radar chart (0-1 scale)
    features = ['pm25', 'green_space_pct', 'population_density', 'traffic_intensity']
    feature_labels = ['PM2.5', 'Green Space', 'Pop. Density', 'Traffic']

    # Get min/max for normalization
    mins = df_clustered[features].min()
    maxs = df_clustered[features].max()

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    for i, info in enumerate(cluster_info):
        cluster_data = df_clustered[df_clustered['cluster'] == i][features].mean()
        # Normalize to 0-1
        normalized = (cluster_data - mins) / (maxs - mins)
        values = normalized.tolist()
        values += values[:1]  # Complete the circle

        ax.plot(angles, values, 'o-', linewidth=2, label=f"Cluster {i}: {info['name']}",
                color=CLUSTER_COLORS[i])
        ax.fill(angles, values, alpha=0.25, color=CLUSTER_COLORS[i])

    # Add Vienna
    vienna = df_clustered[df_clustered['city'] == 'Vienna'].iloc[0][features]
    vienna_normalized = (vienna - mins) / (maxs - mins)
    values = vienna_normalized.tolist()
    values += values[:1]

    ax.plot(angles, values, 'o-', linewidth=3, label='Vienna',
            color=COLORS['accent'], markersize=8)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_labels, size=11)
    ax.set_title('Cluster Profiles Comparison', size=14, fontweight='bold', y=1.1)
    ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"Radar chart saved to: {save_path}")

    return fig


def generate_all_visualizations():
    """Generate all model visualizations and save to files."""
    # Setup output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'models', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Generating Model Visualizations (Part 1)")
    print("=" * 60)

    # Load data and perform clustering
    print("\n1. Loading data and performing clustering...")
    df = load_city_data()
    X_scaled, features, _ = prepare_clustering_features(df)
    cluster_analysis = find_optimal_clusters(X_scaled)
    df_clustered, kmeans, pca, cluster_info, feature_cols = perform_clustering(df, n_clusters=4)

    # Generate visualizations
    print("\n2. Creating elbow plot...")
    create_elbow_plot(cluster_analysis,
                      save_path=os.path.join(output_dir, 'elbow_plot.png'))

    print("\n3. Creating PCA scatter plot...")
    create_pca_scatter_plot(df_clustered, cluster_info,
                            save_path=os.path.join(output_dir, 'pca_scatter.png'))

    print("\n4. Creating cluster box plots...")
    create_cluster_boxplots(df_clustered, cluster_info,
                            save_path=os.path.join(output_dir, 'cluster_boxplots.png'))

    print("\n5. Creating radar chart (bonus)...")
    create_cluster_profile_radar(df_clustered, cluster_info,
                                 save_path=os.path.join(output_dir, 'cluster_radar.png'))

    # Save clustered data
    print("\n6. Saving clustered data...")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    df_clustered.to_csv(os.path.join(data_dir, 'cities_clustered.csv'), index=False)

    print("\n" + "=" * 60)
    print("All visualizations saved to:", output_dir)
    print("=" * 60)

    return df_clustered


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    generate_all_visualizations()
    print("\nVisualization generation complete!")
