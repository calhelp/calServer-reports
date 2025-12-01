# Fonts for DAkkS reports

JasperStarter already ships the DejaVu fonts and uses them with Identity-H
encoding, so German umlauts and other Unicode glyphs render correctly without
embedding a TTF in this repository.

If you need an additional Unicode font (z. B. Arial oder ein Symbol-Font),
install it via iReport/Jaspersoft Studio as a font extension JAR with
`pdfEncoding="Identity-H"`. Place that JAR next to the JDBC driver used by
JasperStarter so it lands on the classpath at runtime.
