from qgis.core import check, QgsAbstractValidityCheck, QgsLayoutItemLabel, QgsValidityCheckResult
from spellchecker import SpellChecker
import re


@check.register(type=QgsAbstractValidityCheck.TypeLayoutCheck)
def layout_check_spelling(context, feedback):
    layout = context.layout
    results = []
    checker = SpellChecker()
    for i in layout.items():
        if isinstance(i, QgsLayoutItemLabel) and i.currentText:
            tokens = r"\w+"
            misspelled = checker.unknown(re.findall(tokens, i.currentText))
            for word in misspelled:
                res = QgsValidityCheckResult()
                res.type = QgsValidityCheckResult.Warning
                res.title = 'Spelling Error?'
                res.detailedDescription = f'{word} may be misspelled, would {checker.correction(word)} be'
                'a better choice'
                results.append(res)

    return results
