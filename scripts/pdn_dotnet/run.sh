#!/bin/sh
# Read .pdn files with .NET's BinaryFormatter, as paint.net does (Program.cs). Needs the .NET 8 SDK
# (Ubuntu: apt-get install dotnet-sdk-8.0); builds itself into work/pdn_dotnet/ the first time.
# Usage: sh scripts/pdn_dotnet/run.sh FILE.pdn [...]
set -e
here=$(cd "$(dirname "$0")" && pwd)
dll="$here/../../work/pdn_dotnet/bin/Release/net8.0/pdn_dotnet.dll"
if [ ! -f "$dll" ] || [ "$here/Program.cs" -nt "$dll" ]; then
    dotnet build "$here/pdn_dotnet.csproj" -c Release -v quiet -nologo >/dev/null
fi
exec dotnet "$dll" "$@"
