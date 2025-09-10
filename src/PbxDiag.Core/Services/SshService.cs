using Renci.SshNet;
using System;
using System.Threading.Tasks;

namespace PbxDiag.Core.Services;

public class SshService
{
    /// <summary>
    /// Executes a command on a remote device via SSH using username and password authentication.
    /// </summary>
    /// <param name="ipAddress">The IP address of the target device.</param>
    /// <param name="username">The username for authentication.</param>
    /// <param name="password">The password for authentication.</param>
    /// <param name="command">The command to execute.</param>
    /// <returns>The output of the command as a string.</returns>
    public async Task<string> RunCommandAsync(string ipAddress, string username, string password, string command)
    {
        return await Task.Run(() =>
        {
            var connectionInfo = new ConnectionInfo(ipAddress, username, new PasswordAuthenticationMethod(username, password));

            using (var client = new SshClient(connectionInfo))
            {
                try
                {
                    client.Connect();
                    if (!client.IsConnected)
                    {
                        return "Error: SSH client could not connect.";
                    }

                    var sshCommand = client.CreateCommand(command);
                    var result = sshCommand.Execute();

                    if (sshCommand.ExitStatus != 0)
                    {
                        return $"Error: Command exited with status {sshCommand.ExitStatus}. Error output: {sshCommand.Error}";
                    }

                    return result;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[SshService] Exception: {ex.Message}");
                    return $"Error: {ex.Message}";
                }
                finally
                {
                    if (client.IsConnected)
                    {
                        client.Disconnect();
                    }
                }
            }
        });
    }

    // TODO: Implement a method for SSH authentication using a private key.
    // public async Task<string> RunCommandWithKeyAsync(string ipAddress, string username, string privateKey, string command)
}
