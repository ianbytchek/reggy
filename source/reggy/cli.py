from typing import IO

from reggy.matcher import Matcher


class Cli:
    """
    Reggy command-line interface.
    """

    def run(self, argv: [str], in_stream: IO, out_stream: IO, err_stream: IO) -> int:
        """
        Parses and executes reggy commands and returns the status.
        """

        # The program expects exactly one argument – the pattern. The default first one is always the executable path.
        if len(argv) <= 1:
            err_stream.write('Reggy expects one or more matching patterns:\n'
                             '  reggy \'foo %{0}\'\n'
                             '  reggy \'qux %{0S3} baz\'\n')
            return 1

        matcher: Matcher = Matcher()
        patterns: [str] = argv[1:]

        matched_lines: [str] = []
        line_count: int = 0

        is_in_tty: bool = in_stream.isatty()
        is_out_tty: bool = out_stream.isatty()

        # If output stream is a tty (not piped) let the user know how to correctly terminate it. Todo: Doesn't behave particularly well
        # todo: with PyCharm console – it appears to use piped streams with tty, not sure about the best way to handle this…
        if is_in_tty:
            print('Enter the text to match and finish with entering an empty line or the EOF character, typically Ctrl-D in Unix and Ctrl-Z in Windows.\n', file=out_stream)

        for line in in_stream:
            line = line[:-1]

            # In a tty mode allow to exit with an empty line.
            if is_in_tty and line == '':
                break

            line_count += 1

            # A line is considered matched if it gets matched least against one pattern – don't iterate beyond that point.
            for pattern in patterns:
                if matcher.match(pattern, line) is not None:
                    matched_lines.append(line)
                    break

        if is_out_tty:
            print(f'Matched {len(matched_lines)} lines out of total {line_count} provided.', file=out_stream)

        for match in matched_lines:
            print(match, file=out_stream)

        return 0
