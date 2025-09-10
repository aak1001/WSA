using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace PbxDiag.Core.Services;

public class HttpService
{
    // A single, static HttpClient instance is generally recommended for performance.
    private static readonly HttpClient HttpClient = new HttpClient();

    /// <summary>
    /// Performs an HTTP GET request to the specified URL.
    /// </summary>
    /// <param name="url">The URL to make the GET request to.</param>
    /// <returns>The response body as a string, or an error message.</returns>
    public async Task<string> GetAsync(string url)
    {
        try
        {
            // Set a reasonable timeout for the request
            using (var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(10)))
            {
                var response = await HttpClient.GetAsync(url, cts.Token);
                response.EnsureSuccessStatusCode(); // Throws an exception if the status code is not a success code.
                return await response.Content.ReadAsStringAsync();
            }
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"[HttpService] HTTP Request Exception: {ex.Message}");
            return $"Error: HTTP request failed. Status code: {ex.StatusCode}";
        }
        catch (TaskCanceledException)
        {
            return "Error: The request timed out.";
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[HttpService] General Exception: {ex.Message}");
            return $"Error: {ex.Message}";
        }
    }

    // TODO: Implement POST, PUT, DELETE methods as needed.
    // TODO: Add support for custom headers, authentication (e.g., Bearer tokens).
}
