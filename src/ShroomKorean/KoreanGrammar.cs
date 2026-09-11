using System.Text.RegularExpressions;

namespace ShroomKorean;

public static class KoreanGrammar
{
    private static readonly Regex Postposition = new(
        @"(\[(?<target>MULTIPLICITY_[A-Z_]+)\])\[JOINER=(?<word>WORD_[A-Z_]+)\]",
        RegexOptions.Compiled);
    private static readonly Regex Counter = new(@"\[(?<number>P[0-9]*NUM)\](?<unit>장|마리|회)", RegexOptions.Compiled);

    // English joiners inspect the following token. Korean particles instead
    // follow their noun, so inspect the preceding target before native expansion.
    public static string Prepare(string text, Func<string, string?> token, Func<string, string?> word)
    {
        // Damage templates can consist entirely of tokens: their Korean words
        // are expanded later. The reversed joiner pattern identifies our order.
        text = Postposition.Replace(text, match =>
        {
            var target = token(match.Groups["target"].Value);
            if (string.IsNullOrWhiteSpace(target) || target.Trim() == "_")
            {
                if (match.Groups["target"].Value == "MULTIPLICITY_ENEMY" &&
                    match.Groups["word"].Value == "WORD_TO")
                    return "대상에게";
                return match.Groups[1].Value;
            }
            return match.Groups[1].Value + (word(match.Groups["word"].Value) ?? "");
        });
        // The game deliberately omits the count for a single generated card.
        // Omit its Korean counter too; do not invent a numeric value.
        return Counter.Replace(text, match =>
            string.IsNullOrWhiteSpace(token(match.Groups["number"].Value))
                ? "[" + match.Groups["number"].Value + "]" : match.Value);
    }
}
