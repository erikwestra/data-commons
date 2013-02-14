""" dataCommons.shared.lib.annotationParser

    This module implements the logic of parsing annotation search criteria.

    Note that we can describe the annotation criteria syntax in Backus Naur
    Form (BNF), like this:

        <criteria>       ::= "{" <expression> "}"
        <expression>     ::= <term> { <rel_op> <term> }
        <term>           ::= <key> ":" <value>
        <key>            ::= <string>
        <value>          ::= <string>
        <rel_op>         ::= "and" | "or"
"""
from dataCommons.shared.models import Annotation
from django.db.models          import Q

#############################################################################

def parse(criteria):
    """ Attempt to parse a set of annotation search criteria.

        'criteria' is a string containing a set of annotation search criteria.
        This string should consist of one or more "key:value" pairs separated
        by either "AND" or "OR", and the whole string surrounded by "{" and "}"
        characters.

        We attempt to parse the criteria string.  Upon completion, we return a
        (success, result) tuple, where 'success' is True if and only if the
        criteria string could be successfully parsed, and 'result' is either a
        django.db.models.Q object to use to filter the search by the supplied
        annotation values, or a string describing why the criteria could not be
        parsed.
    """
    # Start by checking that the annotation criteria starts and ends with "{"
    # and "}" characters.

    if not criteria.startswith("{"):
        return (False, "Annotation criteria must start with a '{' character.")

    if not criteria.endswith("}"):
        return (False, "Annotation criteria must end with a '}' character.")

    criteria = criteria[1:-1]

    # Parse the remaining string into a series of "terms" (key:value pairs)
    # separated by "relational operators" ("AND" or "OR").

    terms   = []
    rel_ops = []

    expecting = "term"

    for part in criteria.split():
        if expecting == "term":
            if ":" not in part:
                return (False, "Annotation criteria contained " + repr(part) +
                               ", expected a key:value pair")
            key,value = part.split(":", 1)
            terms.append((key, value))
            expecting = "rel_op"
        elif expecting == "rel_op":
            if part.upper() in ["AND", "OR"]:
                rel_ops.append(part.upper())
                expecting = "term"
            else:
                return (False, "Annotation criteria contained " + repr(part) +
                               ', expected "AND" or "OR"')

    if expecting != "rel_op":
        return (False, 'Annotation criteria cannot finish on an "AND" or "OR"')

    # Convert each key/value pair into an Annotation record ID.

    annotation_ids = []
    for key,value in terms:
        try:
            annotation = Annotation.objects.get(annotation=key+":"+value)
        except Annotation.DoesNotExist:
            annotation = None

        if annotation == None:
            annotation_ids.append(None)
        else:
            annotation_ids.append(annotation.id)

    print annotation_ids

    # Finally, build the various "Q" objects out of the supplied query
    # parameters, and join them together to yield a single "Q" object
    # representing the entire annotation query.

    combined_q = None
    for i in range(len(terms)):
        q = Q(postingannotation__annotation_id=annotation_ids[i])

        if combined_q == None:
            combined_q = q
        else:
            if rel_ops[i-1] == "AND":
                combined_q = combined_q & q
            elif rel_ops[i-1] == "OR":
                combined_q = combined_q | q

    if combined_q != None:
        return (True, combined_q)
    else:
        return (False, "Annotation query cannot be empty")

