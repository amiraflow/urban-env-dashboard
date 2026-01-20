"""
K-Means Clustering Analysis for Urban Environmental Quality
Part 1: Model Stage (10 points)

This module performs clustering analysis to group cities by their environmental
characteristics, identifying peer cities with similar environmental profiles.

Methodology:
1. Feature selection: PM2.5, green space %, population density, traffic intensity
2. StandardScaler normalization
3. Elbow method to determine optimal K
4. K-means clustering with K=4
5. PCA for 2D visualization
6. Cluster characterization and Vienna identification
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import os


def load_city_data():
    """Load city summary data from CSV."""
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(data_dir, 'data', 'cities_summary.csv')
    return pd.read_csv(data_path)


def prepare_clustering_features(df):
    """
    Select and normalize features for clustering.

    Features used (chosen for environmental quality assessment):
    - PM2.5: Primary air quality indicator
    - green_space_pct: Urban livability indicator
    - population_density: Urbanization intensity
    - traffic_intensity: Emissions source indicator

    Returns:
        tuple: (feature_matrix, feature_names, scaler)
    """
    feature_cols = ['pm25', 'green_space_pct', 'population_density', 'traffic_intensity']

    # Extract features
    X = df[feature_cols].values

    # Normalize using StandardScaler (z-score normalization)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, feature_cols, scaler


def find_optimal_clusters(X_scaled, max_k=10):
    """
    Use elbow method and silhouette scores to find optimal K.

    Args:
        X_scaled: Normalized feature matrix
        max_k: Maximum number of clusters to test

    Returns:
        dict: Contains inertias, silhouette scores, and suggested optimal K
    """
    inertias = []
    silhouette_scores = []
    K_range = range(2, max_k + 1)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

    # Find elbow point (simplified - look for largest drop in improvement)
    improvements = np.diff(inertias)
    elbow_k = np.argmin(improvements) + 2  # +2 because range starts at 2

    # Also consider silhouette score
    best_silhouette_k = np.argmax(silhouette_scores) + 2

    return {
        'K_range': list(K_range),
        'inertias': inertias,
        'silhouette_scores': silhouette_scores,
        'elbow_k': elbow_k,
        'silhouette_k': best_silhouette_k,
        'suggested_k': 4  # We'll use 4 clusters for good interpretability
    }


def perform_clustering(df, n_clusters=4):
    """
    Perform K-means clustering on city environmental data.

    Args:
        df: DataFrame with city data
        n_clusters: Number of clusters

    Returns:
        tuple: (df_with_clusters, kmeans_model, pca_model, cluster_info)
    """
    # Prepare features
    X_scaled, feature_cols, scaler = prepare_clustering_features(df)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    # Add cluster labels to dataframe
    df_clustered = df.copy()
    df_clustered['cluster'] = cluster_labels

    # Perform PCA for 2D visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_clustered['pca_1'] = X_pca[:, 0]
    df_clustered['pca_2'] = X_pca[:, 1]

    # Calculate cluster centers in original space
    cluster_centers_scaled = kmeans.cluster_centers_
    cluster_centers_original = scaler.inverse_transform(cluster_centers_scaled)

    # Create cluster characterization
    cluster_info = []
    for i in range(n_clusters):
        cluster_mask = df_clustered['cluster'] == i
        cluster_cities = df_clustered[cluster_mask]

        info = {
            'cluster_id': i,
            'n_cities': len(cluster_cities),
            'cities': cluster_cities['city'].tolist(),
            'avg_pm25': cluster_cities['pm25'].mean(),
            'avg_green_space': cluster_cities['green_space_pct'].mean(),
            'avg_density': cluster_cities['population_density'].mean(),
            'avg_traffic': cluster_cities['traffic_intensity'].mean(),
            'center': dict(zip(feature_cols, cluster_centers_original[i])),
        }

        # Name clusters based on characteristics
        if info['avg_pm25'] < 15 and info['avg_green_space'] > 40:
            info['name'] = 'Clean & Green'
            info['description'] = 'Low pollution, high green space'
        elif info['avg_pm25'] > 40:
            info['name'] = 'Industrial/Polluted'
            info['description'] = 'High pollution levels'
        elif info['avg_density'] > 8000:
            info['name'] = 'High Density Urban'
            info['description'] = 'Dense urban areas'
        else:
            info['name'] = 'Moderate Urban'
            info['description'] = 'Balanced environmental profile'

        cluster_info.append(info)

    # Sort cluster info by average PM2.5 (cleanest first)
    cluster_info = sorted(cluster_info, key=lambda x: x['avg_pm25'])

    # Remap cluster labels to match sorted order
    old_to_new = {info['cluster_id']: i for i, info in enumerate(cluster_info)}
    df_clustered['cluster'] = df_clustered['cluster'].map(old_to_new)

    # Update cluster_info with new IDs
    for i, info in enumerate(cluster_info):
        info['cluster_id'] = i

    return df_clustered, kmeans, pca, cluster_info, feature_cols


def get_vienna_cluster_info(df_clustered, cluster_info):
    """Get information about Vienna's cluster and peer cities."""
    vienna_row = df_clustered[df_clustered['city'] == 'Vienna'].iloc[0]
    vienna_cluster = vienna_row['cluster']

    # Get cluster details
    vienna_cluster_info = cluster_info[vienna_cluster]

    # Get peer cities (same cluster, sorted by PM2.5 similarity)
    cluster_cities = df_clustered[df_clustered['cluster'] == vienna_cluster].copy()
    cluster_cities['pm25_diff'] = abs(cluster_cities['pm25'] - vienna_row['pm25'])
    peer_cities = cluster_cities.sort_values('pm25_diff')['city'].tolist()

    return {
        'vienna_cluster': vienna_cluster,
        'cluster_name': vienna_cluster_info['name'],
        'cluster_description': vienna_cluster_info['description'],
        'peer_cities': peer_cities,
        'vienna_pm25': vienna_row['pm25'],
        'cluster_avg_pm25': vienna_cluster_info['avg_pm25'],
    }


def save_clustered_data(df_clustered):
    """Save clustered data to CSV."""
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(data_dir, 'data', 'cities_clustered.csv')
    df_clustered.to_csv(output_path, index=False)
    print(f"Clustered data saved to: {output_path}")
    return output_path


if __name__ == '__main__':
    print("=" * 60)
    print("Urban Environmental Quality - K-Means Clustering Analysis")
    print("=" * 60)

    # Load data
    print("\n1. Loading city data...")
    df = load_city_data()
    print(f"   Loaded {len(df)} cities")

    # Find optimal K
    print("\n2. Finding optimal number of clusters...")
    X_scaled, _, _ = prepare_clustering_features(df)
    cluster_analysis = find_optimal_clusters(X_scaled)
    print(f"   Elbow method suggests: K={cluster_analysis['elbow_k']}")
    print(f"   Best silhouette score at: K={cluster_analysis['silhouette_k']}")
    print(f"   Using K=4 for interpretability")

    # Perform clustering
    print("\n3. Performing K-means clustering...")
    df_clustered, kmeans, pca, cluster_info, features = perform_clustering(df, n_clusters=4)

    # Print cluster summary
    print("\n4. Cluster Summary:")
    print("-" * 60)
    for info in cluster_info:
        print(f"\n   Cluster {info['cluster_id']}: {info['name']}")
        print(f"   - {info['description']}")
        print(f"   - {info['n_cities']} cities")
        print(f"   - Avg PM2.5: {info['avg_pm25']:.1f} ug/m3")
        print(f"   - Avg Green Space: {info['avg_green_space']:.1f}%")
        print(f"   - Sample cities: {', '.join(info['cities'][:5])}")

    # Vienna analysis
    print("\n5. Vienna Analysis:")
    print("-" * 60)
    vienna_info = get_vienna_cluster_info(df_clustered, cluster_info)
    print(f"   Vienna is in Cluster {vienna_info['vienna_cluster']}: {vienna_info['cluster_name']}")
    print(f"   Vienna PM2.5: {vienna_info['vienna_pm25']:.1f} ug/m3")
    print(f"   Cluster average PM2.5: {vienna_info['cluster_avg_pm25']:.1f} ug/m3")
    print(f"   Peer cities: {', '.join(vienna_info['peer_cities'][:8])}")

    # Save results
    print("\n6. Saving results...")
    save_clustered_data(df_clustered)

    # PCA explained variance
    print(f"\n7. PCA Analysis:")
    print(f"   Component 1 explains: {pca.explained_variance_ratio_[0]*100:.1f}% of variance")
    print(f"   Component 2 explains: {pca.explained_variance_ratio_[1]*100:.1f}% of variance")
    print(f"   Total explained: {sum(pca.explained_variance_ratio_)*100:.1f}%")

    print("\n" + "=" * 60)
    print("Clustering analysis complete!")
    print("=" * 60)
