using ShroomKorean;

var words = new Dictionary<string,string> { ["WORD_TO"]="에게", ["WORD_ON"]="의" };
void Check(string name, string input, Dictionary<string,string> tokens, string expected)
{
    var result = KoreanGrammar.Prepare(input, k => tokens.GetValueOrDefault(k), k => words.GetValueOrDefault(k));
    foreach (var token in tokens) result = result.Replace("["+token.Key+"]",token.Value);
    // Native FilterTokens also collapses duplicate spaces after substitution.
    result = System.Text.RegularExpressions.Regex.Replace(result, " {2,}", " ");
    if (result != expected) throw new Exception($"{name}: expected '{expected}', got '{result}'");
    Console.WriteLine("PASS " + name);
}
Check("Stab explicitly names target", "[MULTIPLICITY_ENEMY][JOINER=WORD_TO] [PNUM] 피해",
    new() { ["MULTIPLICITY_ENEMY"]="",["PNUM"]="5" }, "대상에게 5 피해");
Check("Area attack retains target", "[MULTIPLICITY_ENEMY][JOINER=WORD_TO] [PNUM] 피해",
    new() { ["MULTIPLICITY_ENEMY"]="모든 적",["PNUM"]="4" }, "모든 적에게 4 피해");
Check("Self card omits particle", "[MULTIPLICITY_CARD][JOINER=WORD_ON] 피해량 +2",
    new() { ["MULTIPLICITY_CARD"]="" }, " 피해량 +2");
Check("Roast hides singular counter", "<link=mC>토스티</link> [PNUM]장 생성",
    new() { ["PNUM"]="" }, "<link=mC>토스티</link> 생성");
Check("Multiple toasties retain count", "<link=mC>토스티</link> [PNUM]장 생성",
    new() { ["PNUM"]="3" }, "<link=mC>토스티</link> 3장 생성");
Check("Zero is preserved", "카드 [PNUM]장 뽑기", new() { ["PNUM"]="0" }, "카드 0장 뽑기");
Check("English is unchanged", "Deal [PNUM] damage[JOINER=WORD_TO][MULTIPLICITY_ENEMY]",
    new() { ["PNUM"]="4",["MULTIPLICITY_ENEMY"]="" }, "Deal 4 damage[JOINER=WORD_TO]");
Check("Token-only damage template names target", "[MULTIPLICITY_ENEMY][JOINER=WORD_TO] [PNUM][LINKKEY=WORD_DAMAGE]",
    new() { ["MULTIPLICITY_ENEMY"]="",["PNUM"]="4" }, "대상에게 4[LINKKEY=WORD_DAMAGE]");
Check("Explicit self remains self", "[MULTIPLICITY_ENEMY][JOINER=WORD_TO] [PNUM] 피해",
    new() { ["MULTIPLICITY_ENEMY"]="자신",["PNUM"]="2" }, "자신에게 2 피해");
Check("Underscore omission names target", "[MULTIPLICITY_ENEMY][JOINER=WORD_TO] [PNUM] 피해",
    new() { ["MULTIPLICITY_ENEMY"]="_",["PNUM"]="5" }, "대상에게 5 피해");
