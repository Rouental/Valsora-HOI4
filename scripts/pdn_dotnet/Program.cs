// Read a .pdn's object graph with .NET's own BinaryFormatter, the reader paint.net opens .pdn files with, and with
// .NET 9's NrbfDecoder (2026-10-18: our flag files passed pdn_check.py but paint.net refused them; BinaryFormatter
// said "An object cannot be registered twice"). paint.net's classes are stood in for by one class that keeps what
// it is given, so only the graph is tested, not the pixels after it (pdn_check.py checks those).
//     sh scripts/pdn_dotnet/run.sh FILE.pdn [...]    -> "ok" per file, or the reader's error; exit code = failures
using System;
using System.IO;
using System.Linq;
using System.Formats.Nrbf;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;

#pragma warning disable SYSLIB0011, SYSLIB0050, SYSLIB0051
[Serializable]
public class Stub : ISerializable {
    public SerializationInfo Info;
    protected Stub(SerializationInfo info, StreamingContext ctx) { Info = info; }
    public void GetObjectData(SerializationInfo info, StreamingContext ctx) {}
}

sealed class Binder : SerializationBinder {
    public override Type BindToType(string asm, string type) => type.StartsWith("PaintDotNet") ? typeof(Stub) : null;
}

public static class Program {
    static int Main(string[] args) {
        int bad = 0;
        foreach (var path in args) {
            var buf = File.ReadAllBytes(path);
            int n = buf[4] | (buf[5] << 8) | (buf[6] << 16);
            int g0 = 7 + n + 2;  // after "PDN3", the XML header and paint.net's two-byte marker
            var problems = new System.Collections.Generic.List<string>();
            try {
                using var ms = new MemoryStream(buf, g0, buf.Length - g0);
                NrbfDecoder.Decode(ms, leaveOpen: true);
            } catch (Exception e) { problems.Add("NrbfDecoder: " + e.Message); }
            try {
                using var ms = new MemoryStream(buf, g0, buf.Length - g0);
                var doc = (Stub)new BinaryFormatter { Binder = new Binder() }.Deserialize(ms);
                var list = (Stub)doc.Info.GetValue("layers", typeof(object));
                var items = ((object[])list.Info.GetValue("ArrayList+_items", typeof(object[]))).Where(x => x != null).Count();
                if (items != list.Info.GetInt32("ArrayList+_size"))
                    problems.Add($"BinaryFormatter: {items} layers in the list's items, its size says {list.Info.GetInt32("ArrayList+_size")}");
            } catch (Exception e) { problems.Add("BinaryFormatter: " + e.Message); }
            bad += problems.Count > 0 ? 1 : 0;
            Console.WriteLine(path + ": " + (problems.Count == 0 ? "ok" : "\n  " + string.Join("\n  ", problems)));
        }
        return bad;
    }
}
