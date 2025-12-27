using CareerNavigator.Core.Models.Schema;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System.Threading;

namespace CareerNavigator.Core.Engines;

public class UniverseProvider : IUniverseProvider, IDisposable
{
    private Universe _universe = null!;
    private readonly string _filePath;
    private readonly FileSystemWatcher? _watcher;
    private readonly ILogger<UniverseProvider> _logger;
    private readonly Lock _lock = new();

    public UniverseProvider(IWebHostEnvironment env, ILogger<UniverseProvider> logger)
    {
        _logger = logger;
        _filePath = Path.Combine(env.ContentRootPath, "Data", "universe.json");

        LoadUniverse();

        // Setup File Watcher for Live Updates
        try
        {
            var directory = Path.GetDirectoryName(_filePath);
            if (directory != null && Directory.Exists(directory))
            {
                _watcher = new FileSystemWatcher(directory, "universe.json");
                _watcher.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.Size;
                _watcher.Changed += OnFileChanged;
                _watcher.Created += OnFileChanged;
                _watcher.EnableRaisingEvents = true;
                _logger.LogInformation("🌍 Universe File Watcher Active on: {Path}", _filePath);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize FileSystemWatcher");
        }
    }

    private void OnFileChanged(object sender, FileSystemEventArgs e)
    {
        // Debounce slightly to avoid read locks during write
        Thread.Sleep(500);
        LoadUniverse();
    }

    private void LoadUniverse()
    {
        lock (_lock)
        {
            if (!File.Exists(_filePath))
            {
                _universe = new Universe();
                _logger.LogWarning("⚠️ Universe file not found at {Path}", _filePath);
                return;
            }

            try
            {
                var json = File.ReadAllText(_filePath);
                var settings = new JsonSerializerSettings
                {
                    ContractResolver = new CamelCasePropertyNamesContractResolver(),
                    NullValueHandling = NullValueHandling.Ignore
                };
                _universe = JsonConvert.DeserializeObject<Universe>(json, settings) ?? new Universe();
                _logger.LogInformation("✅ Universe Loaded: {NodeCount} Nodes, {LinkCount} Links",
                    _universe.Nodes.Count, _universe.Links.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Failed to load Universe.json");
                _universe = new Universe();
            }
        }
    }

    public Universe GetUniverse() => _universe;

    /// <summary>
    /// Returns a list of Node IDs directly connected to the specified node.
    /// </summary>
    public List<string> GetNeighbors(string nodeId)
    {
        // 1. Safety Check: If universe isn't loaded, return empty list
        if (_universe == null)
        {
            return new List<string>();
        }

        List<string> neighborList = new List<string>();

        // 2. Iterate through all links in the database
        foreach (var link in _universe.Links)
        {
            // We need to check both directions because connections are bidirectional
            bool isSourceMatch = string.Equals(link.Source, nodeId, StringComparison.OrdinalIgnoreCase);
            bool isTargetMatch = string.Equals(link.Target, nodeId, StringComparison.OrdinalIgnoreCase);

            if (isSourceMatch)
            {
                // If I am the Source, the Neighbor is the Target
                neighborList.Add(link.Target);
            }
            else if (isTargetMatch)
            {
                // If I am the Target, the Neighbor is the Source
                neighborList.Add(link.Source);
            }
        }

        // 3. Remove Duplicates
        // Using HashSet is the cleanest way to ensure uniqueness
        HashSet<string> uniqueNeighbors = new HashSet<string>(neighborList, StringComparer.OrdinalIgnoreCase);

        return uniqueNeighbors.ToList();
    }

    /// <summary>
    /// Finds the shortest path between two skills using Breadth-First Search (BFS).
    /// </summary>
    public List<string> GetShortestPath(string startId, string endId)
    {
        if (_universe == null) return new List<string>();

        var start = startId.ToLower();
        var end = endId.ToLower();

        if (start == end) return new List<string> { start };

        var queue = new Queue<List<string>>();
        queue.Enqueue(new List<string> { start });

        var visited = new HashSet<string> { start };

        while (queue.Count > 0)
        {
            var path = queue.Dequeue();
            var node = path.Last();

            if (node == end) return path;

            var neighbors = GetNeighbors(node);
            foreach (var neighbor in neighbors)
            {
                var neighborLower = neighbor.ToLower();
                if (!visited.Contains(neighborLower))
                {
                    visited.Add(neighborLower);
                    var newPath = new List<string>(path) { neighborLower };
                    queue.Enqueue(newPath);
                }
            }
        }

        return new List<string>(); // No path found
    }

    public void Dispose()
    {
        _watcher?.Dispose();
    }
}