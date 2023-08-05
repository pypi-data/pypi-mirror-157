package fpp.compiler.codegen

import fpp.compiler.analysis._
import fpp.compiler.ast._
import fpp.compiler.util._

/** ====================================================================== 
 *  Computes the names of the C++ files to generate
 *  Checks for duplicates that would cause a name collision. 
 *  ======================================================================*/
object ComputeCppFiles extends AstStateVisitor {

  type State = Map[String, Option[Location]]

  /** Names of generated C++ files */
  object FileNames {

    /** Gets the C++ file name for generated constants */
    def getConstants = "FppConstantsAc"

    /** Gets the C++ file name for generated topologies */
    def getTopology(baseName: String): String = s"${baseName}TopologyAc"

  }

  override def defComponentAnnotatedNode(
    s: State,
    aNode: Ast.Annotated[AstNode[Ast.DefComponent]]
  ) = {
    val node = aNode._2
    val data = node.data
    visitList(s, data.members, matchComponentMember)
  }

  override def defConstantAnnotatedNode(
    s: State,
    aNode: Ast.Annotated[AstNode[Ast.DefConstant]]
  ) = addMappings(s, FileNames.getConstants, None)

  override def defModuleAnnotatedNode(
    s: State,
    aNode: Ast.Annotated[AstNode[Ast.DefModule]]
  ) = {
    val node = aNode._2
    val data = node.data
    visitList(s, data.members, matchModuleMember)
  }

  override def defTopologyAnnotatedNode(
    s: State,
    aNode: Ast.Annotated[AstNode[Ast.DefTopology]]
  ) = {
    val node = aNode._2
    val name = node.data.name
    val loc = Locations.get(node.id)
    addMappings(s, FileNames.getTopology(name), Some(loc))
  }

  override def transUnit(s: State, tu: Ast.TransUnit) =
    visitList(s, tu.members, matchTuMember)

  /** Adds mappings for hpp and cppfiles */
  private def addMappings(
    s: State,
    fileName: String,
    locOpt: Option[Location]
  ) = {
    for {
      s <- addHppMapping(s, fileName, locOpt)
      s <- addCppMapping(s, fileName, locOpt)
    }
    yield s
  }

  /** Adds a mapping for an hpp file  */
  private def addHppMapping(
    s: State,
    fileName: String,
    locOpt: Option[Location]
  ) =
    addMapping(s, (s"$fileName.hpp" -> locOpt))

  /** Adds a mapping for a cpp file  */
  private def addCppMapping(
    s: State,
    fileName: String,
    locOpt: Option[Location]
  ) = addMapping(s, (s"$fileName.cpp" -> locOpt))

  /** Adds a mapping for one file */
  private def addMapping(
    s: State,
    mapping: (String, Option[Location])
  ) = {
    val (fileName, locOpt) = mapping
    (s.get(fileName), locOpt) match {
      case (Some(Some(prevLoc)), Some(loc)) =>
        Left(CodeGenError.DuplicateCppFile(fileName, loc, prevLoc))
      case _ => Right(s + mapping)
    }
  }

}
