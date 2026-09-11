using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using BepInEx;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.Localization.Tables;

namespace ShroomKorean;

[BepInPlugin("community.shroomandgloom.korean", "Shroom and Gloom Korean", "0.1.0")]
public sealed class Plugin : BasePlugin
{
    internal static Plugin Instance = null!;
    internal static Dictionary<string, Translation> Entries = new(StringComparer.Ordinal);
    private static readonly HashSet<string> Reported = new(StringComparer.Ordinal);
    private static readonly HashSet<int> Fonts = new();
    private static TMP_FontAsset? koreanFont;
    private static AssetBundle? fontBundle;
    private static bool loadingFont;
    private static int translatedCount;
    internal static string DataDirectory = "";

    public override void Load()
    {
        Instance = this;
        if (!Config.Bind("General", "Enabled", true, "Apply Korean on the English game language. Restart after changing.").Value)
            return;
        DataDirectory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)!;
        Entries = JsonSerializer.Deserialize<Dictionary<string, Translation>>(
            File.ReadAllText(Path.Combine(DataDirectory, "translations.json")))
            ?? throw new InvalidDataException("Empty Korean translation catalog.");
        var harmony = new Harmony("community.shroomandgloom.korean");
        // Localize before SmartFormat and game token substitution. Preserve link IDs.
        foreach (var method in typeof(StringTableEntry).GetMethods(BindingFlags.Public | BindingFlags.Instance)
                     .Where(m => m.Name == "GetLocalizedString" && !m.IsGenericMethod))
            harmony.Patch(method, prefix: new HarmonyMethod(typeof(Plugin), nameof(TranslateEntry)));
        foreach (var type in new[] { typeof(TextMeshPro), typeof(TextMeshProUGUI) })
            harmony.Patch(AccessTools.Method(type, "OnEnable"), postfix: new HarmonyMethod(typeof(Plugin), nameof(PrepareFont)));
        var helpers = Assembly.Load("Assembly-CSharp").GetType("LocalizationHelpers", throwOnError: true)!;
        harmony.Patch(AccessTools.Method(helpers, "FilterTokens"),
            prefix: new HarmonyMethod(typeof(Plugin), nameof(PrepareKoreanGrammar)));
        Log.LogInfo($"Korean catalog loaded: {Entries.Count} entries. Target: EA 0.6.21 / Steam build 25221077.");
    }

    public sealed class Translation
    {
        public string SourceHash { get; set; } = "";
        public string Text { get; set; } = "";
    }

    private static void PrepareKoreanGrammar(ref string __0,
        Il2CppSystem.Collections.Generic.IReadOnlyDictionary<string, string> __1)
    {
        if (string.IsNullOrEmpty(__0) || __1 == null) return;
        try
        {
            if (UnityEngine.Localization.Settings.LocalizationSettings.SelectedLocale?.Identifier.Code != "en") return;
            __0 = KoreanGrammar.Prepare(__0,
                key => __1.TryGetValue("[" + key + "]", out var value) ? value
                    : __1.TryGetValue(key, out value) ? value : null,
                key => Entries.TryGetValue("Card/" + key, out var entry) ? entry.Text : null);
        }
        catch (Exception ex)
        {
            if (Reported.Add("grammar-error")) Instance.Log.LogError(ex);
        }
    }

    private static void TranslateEntry(StringTableEntry __instance)
    {
        try
        {
            if (__instance.Table.LocaleIdentifier.Code != "en") return;
            var entryKey = __instance.Key;
            var key = __instance.Table.TableCollectionName + "/" + (string.IsNullOrEmpty(entryKey) ? "@" + __instance.KeyId : entryKey);
            if (!Entries.TryGetValue(key, out var translation))
            {
                if (Reported.Add(key)) Instance.Log.LogDebug("Untranslated key: " + key);
                return;
            }
            var current = __instance.Value;
            if (current == translation.Text) return;
            var hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(current ?? ""))).ToLowerInvariant();
            if (hash != translation.SourceHash)
            {
                if (Reported.Add(key)) Instance.Log.LogWarning("Original text changed; kept original: " + key);
                return;
            }
            // The value setter invalidates the SmartFormat cache.
            __instance.Value = translation.Text;
            if (++translatedCount <= 5) Instance.Log.LogInfo("Translated table entry: " + key);
        }
        catch (Exception ex)
        {
            if (Reported.Add("entry-error:" + ex.GetType().Name)) Instance.Log.LogError(ex);
        }
    }

    private static void PrepareFont(TMP_Text __instance)
    {
        if (loadingFont) return;
        try
        {
            if (koreanFont == null)
            {
                loadingFont = true;
                fontBundle = AssetBundle.LoadFromFile(Path.Combine(DataDirectory, "shroom-korean-jua"));
                if (fontBundle == null) throw new IOException("Could not load Korean font bundle.");
                koreanFont = fontBundle.LoadAsset<TMP_FontAsset>("assets/jua-korean-sdf.asset");
                if (koreanFont == null) throw new IOException("Korean TMP font is missing.");
                UnityEngine.Object.DontDestroyOnLoad(koreanFont);
                if (__instance.font != null && __instance.font.material != null)
                    koreanFont.material.shader = __instance.font.material.shader;
                koreanFont.ReadFontAssetDefinition();
                Instance.Log.LogInfo($"Korean font loaded: {koreanFont.name}, {koreanFont.characterTable.Count} characters.");
            }
            var original = __instance.font;
            if (original != null && original != koreanFont && Fonts.Add(original.GetInstanceID()))
            {
                original.fallbackFontAssetTable ??= new Il2CppSystem.Collections.Generic.List<TMP_FontAsset>();
                original.fallbackFontAssetTable.Insert(0, koreanFont);
            }
        }
        catch (Exception ex)
        {
            if (Reported.Add("font-error")) Instance.Log.LogError(ex);
        }
        finally { loadingFont = false; }
    }
}
