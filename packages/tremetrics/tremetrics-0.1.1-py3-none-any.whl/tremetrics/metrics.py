import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.utils.multiclass import unique_labels


class ConfusionMatrix:

    def __init__(self, y_true=None, y_pred=None):
        self.y_true_ = y_true
        self.y_pred_ = y_pred
        self.labels_ = None

    @staticmethod
    def unique_labels(*ys):
        return unique_labels(*ys)

    @classmethod
    def from_pred(cls, y_true, y_pred):
        cm = ConfusionMatrix()
        cm.y_true_ = y_true
        cm.y_pred_ = y_pred
        return cm

    def set_labels(self, labels):
        self.labels_ = labels
        return self

    def _get_matrix(self, labels=None):
        if self.y_true_ is not None and self.y_pred_ is not None:
            return metrics.confusion_matrix(self.y_true_, self.y_pred_, labels=labels)
        else:
            raise ValueError("No y_true or y_pred specified. "
                             "Use ConfusionMatrix.from_pred(y_true, y_pred) as constructor.")

    def _get_binary_matrix(self):
        try:
            return self._get_matrix(labels=[1, 0])
        except ValueError as e:
            if str(e) != "At least one label specified must be in y_true": raise e
            else:
                try:
                    return self._get_matrix(labels=[True, False])
                except ValueError as e:
                    if str(e) != "At least one label specified must be in y_true": raise e
                    else:
                        raise ValueError("Input is not binary. Use (0, 1) or boolean values instead.")

    @property
    def matrix(self):
        if self.labels_ is None:
            # Try to make sure True Positives are in the upper-left.
            # Otherwise, default to standard sklearn sorted order.
            try:
                return self._get_binary_matrix()
            except ValueError as e:
                if str(e) != "Input is not binary. Use (0, 1) or boolean values instead.": raise e
                else:
                    return self._get_matrix()
        else:
            return self._get_matrix(labels=self.labels_)

    def __repr__(self):
        raise repr(self.matrix)

    @property
    def _values(self):
        """
        Get binary matrix values as a contiguous flattened array.
        Returns
        -------
        y : ndarray
            A 1-D array containing binary matrix values.
        """
        return self._get_binary_matrix().ravel()

    @property
    def tp(self):
        """
        True positives (TP).
        """
        return self._values[0]

    @property
    def fn(self):
        """
        False negatives (FN).
        """
        return self._values[1]

    @property
    def fp(self):
        """
        False positives (FP).
        """
        return self._values[2]

    @property
    def tn(self):
        """
        True negatives (TN).
        """
        return self._values[3]

    def get_latex_table(self, multirow=True):
        """
        Generate Latex code to insert this confusion matrix as a table.

        Parameters
        ----------
        multirow : bool, default=True
            Whether to use the Latex package ``multirow``, which is needed for rotating the left-hand table labels.
            If so, include ``\usepackage{multirow}`` in your Latex preamble.

        Returns
        -------
        code : str
            Latex code to use in your tex file.
        """
        if multirow:
            actual = "\\multirow[c]{2}{*}{\\rotatebox[origin=center]{90}{Actual}}"
        else:
            actual = "{Actual}"

        code = "\\begin{tabular}{cc|cc}\n" \
               "\\multicolumn{2}{c}{} & \\multicolumn{2}{c}{Predicted} \\\\\n" \
               "& & Positive & Negative \\\\\n" \
               "\\cline{2-4}\n" \
               "%(actual)s\n" \
               "& Positive & %(tp)d & %(fn)d \\\\[1ex]\n" \
               "& Negative & %(fp)d & %(tn)d \\\\\n" \
               "\\cline{2-4}\n" \
               "\\end{tabular}" % {'tp': self.tp, 'fn': self.fn, 'fp': self.fp, 'tn': self.tn, 'actual': actual}
        return code

    def plot(self, ax=None, cmap=plt.cm.Blues):
        if self.labels_ is None:
            try:
                return metrics.ConfusionMatrixDisplay(self._get_binary_matrix(), display_labels=[True, False]).plot(ax=ax, cmap=cmap)
            except ValueError: pass
        return metrics.ConfusionMatrixDisplay(self.matrix, display_labels=self.unique_labels(self.y_true_, self.y_pred_)).plot(ax=ax, cmap=cmap)
