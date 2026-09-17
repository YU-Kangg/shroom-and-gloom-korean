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

[BepInPlugin("community.shroomandgloom.korean", "Shroom and Gloom Korean", "0.1.3")]
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
    private static int repairedCardCount;
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
        harmony.Patch(AccessTools.Method(typeof(TextMeshPro), "GenerateTextMesh"),
            postfix: new HarmonyMethod(typeof(Plugin), nameof(RestoreCardTextLayers)));
        var gameAssembly = Assembly.Load("Assembly-CSharp");
        var helpers = gameAssembly.GetType("LocalizationHelpers", throwOnError: true)!;
        harmony.Patch(AccessTools.Method(helpers, "FilterTokens"),
            prefix: new HarmonyMethod(typeof(Plugin), nameof(PrepareKoreanGrammar)));
        harmony.Patch(AccessTools.Method(typeof(Tooltip), "GetTooltip"),
            prefix: new HarmonyMethod(typeof(Plugin), nameof(UseForgetButtonTooltip)));
        harmony.Patch(AccessTools.Method(typeof(ModifyCardEncounterUI), "RefreshTrainingTypeText"),
            prefix: new HarmonyMethod(typeof(Plugin), nameof(PrepareUpgradeText)));
        harmony.Patch(AccessTools.Method(typeof(BowlShopEncounterUI), "CalculateCanAffordAndDisplay"),
            prefix: new HarmonyMethod(typeof(Plugin), nameof(PrepareShopText)));
        Log.LogInfo("Korean card text renderer layer repair enabled.");
        Log.LogInfo($"Korean catalog loaded: {Entries.Count} entries. Target: EA 0.6.39 / Steam build 25342632.");
    }

    private static void PrepareUpgradeText(ModifyCardEncounterUI __instance)
    {
        UseUnifiedUiFont(__instance._detailText);
    }

    private static void PrepareShopText(BowlShopEncounterUI __instance)
    {
        UseUnifiedUiFont(__instance.CanAffordText);
        UseUnifiedUiFont(__instance.CanAffordCanBeReusedText);
    }

    private static void UseUnifiedUiFont(TMP_Text? text)
    {
        try
        {
            if (text == null || UnityEngine.Localization.Settings.LocalizationSettings.SelectedLocale?.Identifier.Code != "en") return;
            if (koreanFont == null) PrepareFont(text);
            if (koreanFont == null || text.font == koreanFont) return;
            // These mixed labels previously rendered ASCII and Korean using separate
            // font/material meshes. The bundled font includes digits and decimal points.
            text.font = koreanFont;
            text.fontSharedMaterial = koreanFont.material;
            if (Reported.Add("unified-ui:" + text.GetInstanceID()))
                Instance.Log.LogInfo("Applied unified Korean/number font to " + text.name);
        }
        catch (Exception ex)
        {
            if (Reported.Add("unified-ui-error")) Instance.Log.LogError(ex);
        }
    }

    private static void RestoreCardTextLayers(TextMeshPro __instance)
    {
        try
        {
            // Korean fallback glyphs are rendered by TMP_SubMesh objects. A submesh can be
            // created after the game snapshots renderers for a temporary UI layer, leaving
            // it on that layer when the pooled card is reused. GenerateTextMesh runs before
            // rendering, so matching the parent here repairs both new and reused cards.
            var repaired = 0;
            foreach (var subMesh in __instance.GetComponentsInChildren<TMP_SubMesh>(includeInactive: true))
            {
                var text = subMesh.textComponent;
                if (text == null || subMesh.gameObject.layer == text.gameObject.layer) continue;
                subMesh.gameObject.layer = text.gameObject.layer;
                repaired++;
            }
            if (repaired > 0 && repairedCardCount++ < 5)
                Instance.Log.LogInfo($"Repaired {repaired} Korean card text renderer layer(s).");
        }
        catch (Exception ex)
        {
            if (Reported.Add("card-text-layer-repair:" + ex.GetType().Name)) Instance.Log.LogError(ex);
        }
    }

    private static bool UseForgetButtonTooltip(Tooltip __instance, ref string __result)
    {
        // Resolve at hover time from this exact button. Updating the shop's cached static
        // tooltip does not cover every tooltip source or initialization order.
        try
        {
            if (UnityEngine.Localization.Settings.LocalizationSettings.SelectedLocale?.Identifier.Code != "en") return true;
            var button = __instance.GetComponent<SwapOutObjectButton>();
            var calls = button?.OnClickUEvent?.m_PersistentCalls?.m_Calls;
            if (calls == null) return true;
            CardTrainingType? chosen = null;
            foreach (var call in calls)
            {
                if (call.m_MethodName != "HandleModifyCardClick"
                    || call.m_Target?.TryCast<BowlShopEncounterUI>() == null
                    || call.m_Mode != UnityEngine.Events.PersistentListenerMode.Object
                    || call.m_CallState == UnityEngine.Events.UnityEventCallState.Off) continue;
                var argument = call.m_Arguments?.m_ObjectArgument?.TryCast<CardTrainingType>();
                if (argument == null || (argument != CardTrainingType.TForgetExploreCard
                    && argument != CardTrainingType.TForgetCombatCard)) continue;
                if (chosen != null && chosen != argument) return true;
                chosen = argument;
            }
            if (chosen == null) return true;
            __result = LocalizationHelpers.FilterCommonWordLinkKey(chosen.GetTrainingTypeDetail());
            if (Reported.Add("forget-tooltip:" + __instance.GetInstanceID()))
                Instance.Log.LogInfo($"Forget tooltip: button={button!.name}; action={chosen.name}; text={__result}");
            return false;
        }
        catch (Exception ex)
        {
            if (Reported.Add("forget-tooltip")) Instance.Log.LogError(ex);
            return true;
        }
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
