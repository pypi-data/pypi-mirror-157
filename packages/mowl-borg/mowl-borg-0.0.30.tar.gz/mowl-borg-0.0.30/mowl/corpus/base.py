from org.semanticweb.owlapi.manchestersyntax.renderer import ManchesterOWLSyntaxOWLObjectRendererImpl
from org.semanticweb.owlapi.model import OWLLiteral
from org.semanticweb.owlapi.search import EntitySearcher


from jpype.types import *

from org.mowl import MOWLShortFormProvider
import logging



def extract_and_save_axiom_corpus(ontology, out_file, mode = "w"):
    """Method to extract axioms of a particular ontology and save it into a file.
    :param ontology: OWL ontology from which the axioms will be extracted.
    :type ontology: OWLOntology
    :param out_file: File path to save the extracted axioms.
    :type out_file: str
    :param mode: mode for opening the `out_file`, defaults to `"w"`
    :type mode: str(,optional)
    """
    
    logging.info("Generating axioms corpus")
    renderer = ManchesterOWLSyntaxOWLObjectRendererImpl()
    shortFormProvider = MOWLShortFormProvider()
    renderer.setShortFormProvider(shortFormProvider)
    with open(out_file, mode) as f:
        for owl_class in ontology.getClassesInSignature():
            axioms = ontology.getAxioms(owl_class)
            for axiom in axioms:
                rax = renderer.render(axiom)
                rax = rax.replaceAll(JString("[\\r\\n|\\r|\\n()|<|>]"), JString(""))
                f.write(f'{rax}\n')

def extract_axiom_corpus(ontology):
    """Method to extract axioms of a particular ontology. Similar to :func:`extract_and_save_axiom_corpus` but this method returns a list instead saving into a file.
    :param ontology: OWL ontology from which the axioms will be extracted.
    :type ontology: OWLOntology
    """    

    logging.info("Generating axioms corpus")
    renderer = ManchesterOWLSyntaxOWLObjectRendererImpl()
    shortFormProvider = MOWLShortFormProvider()
    renderer.setShortFormProvider(shortFormProvider)

    corpus = []
    
    for owl_class in ontology.getClassesInSignature():
        axioms = ontology.getAxioms(owl_class)
        for axiom in axioms:
            rax = renderer.render(axiom)
            rax = rax.replaceAll(JString("[\\r\\n|\\r|\\n()|<|>]"), JString(""))
            corpus.append(rax)
    return corpus



def extract_and_save_annotation_corpus(ontology, out_file, mode):
    """Method to extract annotations of a particular ontology and save it into a file.
    :param ontology: OWL ontology from which the annotations will be extracted.
    :type ontology: OWLOntology
    :param out_file: File path to save the extracted annotations.
    :type out_file: str
    :param mode: mode for opening the `out_file`, defaults to `"w"`
    :type mode: str(,optional)
    """

    logging.info("Generating annotation corpus")
    with open(out_file, mode) as f:
        for owl_class in ontology.getClassesInSignature():
            cls = str(owl_class)
              
            annotations = EntitySearcher.getAnnotations(owl_class, ontology)
            for annotation in annotations:
                if isinstance(annotation.getValue(), OWLLiteral):
                    obj_property = str(annotation.getProperty()).replace("\n", " ")
                    # could filter on property
                    value = str(annotation.getValue().getLiteral()).replace("\n", " ")
                    f.write(f'{cls} {obj_property} {value}\n')



def extract_annotation_corpus(ontology):
    """Method to extract annotations of a particular ontology. Similar to :func:`extract_and_save_annotation_corpus` but this method returns a list instead saving into a file.
    :param ontology: OWL ontology from which the annotations will be extracted.
    :type ontology: OWLOntology
    """    

    logging.info("Generating annotation corpus")

    corpus = []
    for owl_class in ontology.getClassesInSignature():
        cls = str(owl_class)

        annotations = EntitySearcher.getAnnotations(owl_class, ontology)
        for annotation in annotations:
            if isinstance(annotation.getValue(), OWLLiteral):
                obj_property = str(annotation.getProperty()).replace("\n", " ")
                # could filter on property
                value = str(annotation.getValue().getLiteral()).replace("\n", " ")
                corpus.append(f'{cls} {obj_property} {value}\n')

    return corpus
