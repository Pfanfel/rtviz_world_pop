using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.Data.SQLite;
using Dapper;
using System.Collections.Generic;
using System.Threading.Tasks;

var builder = WebApplication.CreateBuilder(args);

// Add CORS services to the container
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Enable CORS middleware
app.UseCors();

// SQLite connection string
string connectionString = "Data Source=../src/data/quadkeyDB.sqlite;Version=3;";

// Middleware to log request processing time
app.Use(async (context, next) =>
{
    var startTime = System.Diagnostics.Stopwatch.StartNew();
    await next.Invoke();
    startTime.Stop();
    Console.WriteLine($"Request to {context.Request.Path} took {startTime.ElapsedMilliseconds}ms");
});

// Route to get tile data
app.MapGet("/api/male/{z}/{y}/{x}", async (int z, int y, int x) =>
{
    Console.WriteLine($"Requesting tile: z={z}, y={y}, x={x}");

    // Compute the list of quadkeys for children at the desired level
    var parentQuadkey = ComputeQuadKey(z, x, y); // Function to generate quadkey
    var childrenQuadKeys = GetChildrenQuadKeys(parentQuadkey, z + 5); // Adjust as needed

    // Fetch data from SQLite
    var results = await FetchDataFromDb(childrenQuadKeys, connectionString);

    return Results.Ok(results);
});

// Route to get database schema
app.MapGet("/api/schema", async () =>
{
    using var connection = new SQLiteConnection(connectionString);
    var tables = await connection.QueryAsync<string>("SELECT name FROM sqlite_master WHERE type='table';");
    return Results.Ok(tables);
});

// Helper function to compute the quadkey
static string ComputeQuadKey(int zoomLevel, int x, int y)
{
    var quadkey = new System.Text.StringBuilder();
    for (int i = zoomLevel; i > 0; i--)
    {
        int digit = 0;
        int mask = 1 << (i - 1);
        if ((x & mask) != 0) digit++;
        if ((y & mask) != 0) digit += 2;
        quadkey.Append(digit);
    }
    return quadkey.ToString();
}

// Helper function to generate child quadkeys
static IEnumerable<string> GetChildrenQuadKeys(string parentQuadkey, int depth)
{
    var children = new List<string>();
    var stack = new Stack<string>();
    stack.Push(parentQuadkey);

    while (stack.Count > 0)
    {
        var current = stack.Pop();
        if (current.Length < depth)
        {
            for (int i = 0; i < 4; i++)
            {
                stack.Push(current + i);
            }
        }
        else
        {
            children.Add(current);
        }
    }

    return children;
}

// Helper function to fetch data from SQLite
static async Task<IEnumerable<dynamic>> FetchDataFromDb(IEnumerable<string> quadkeys, string connectionString)
{
    using var connection = new SQLiteConnection(connectionString);
    var query = @"
        SELECT quadkey, raster_1
        FROM data_slice_male_long_lat
        WHERE quadkey IN @Quadkeys";
    var results = await connection.QueryAsync<dynamic>(query, new { Quadkeys = quadkeys });
    return results;
}

app.Run();
