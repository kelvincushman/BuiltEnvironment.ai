import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import TurndownService from 'turndown'

/**
 * Export document content to PDF
 */
export async function exportToPDF(content: string, fileName: string): Promise<void> {
  try {
    // Create a temporary container
    const container = document.createElement('div')
    container.style.position = 'absolute'
    container.style.left = '-9999px'
    container.style.width = '210mm' // A4 width
    container.style.padding = '20mm'
    container.style.backgroundColor = 'white'
    container.style.color = 'black'
    container.innerHTML = content
    document.body.appendChild(container)

    // Convert to canvas
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    })

    // Remove temporary container
    document.body.removeChild(container)

    // Create PDF
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth
    const imgHeight = (canvas.height * pageWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    // Add additional pages if content is longer than one page
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    // Save PDF
    pdf.save(`${fileName}.pdf`)
  } catch (error) {
    console.error('Error exporting to PDF:', error)
    throw new Error('Failed to export to PDF')
  }
}

/**
 * Export document content to Markdown
 */
export function exportToMarkdown(content: string, fileName: string): void {
  try {
    const turndownService = new TurndownService({
      headingStyle: 'atx',
      codeBlockStyle: 'fenced',
      bulletListMarker: '-',
    })

    // Add custom rules for highlights
    turndownService.addRule('highlight', {
      filter: ['mark'],
      replacement: (content) => `==${content}==`,
    })

    // Convert HTML to Markdown
    const markdown = turndownService.turndown(content)

    // Create blob and download
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${fileName}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting to Markdown:', error)
    throw new Error('Failed to export to Markdown')
  }
}

/**
 * Export document content to HTML
 */
export function exportToHTML(content: string, fileName: string): void {
  try {
    // Create a complete HTML document
    const htmlDocument = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${fileName}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
      color: #1f2937;
    }
    h1 { font-size: 2rem; font-weight: bold; margin-bottom: 1rem; }
    h2 { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.75rem; margin-top: 1.5rem; }
    h3 { font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; margin-top: 1rem; }
    h4 { font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 0.75rem; }
    p { margin-bottom: 1rem; }
    ul, ol { padding-left: 1.5rem; margin-bottom: 1rem; }
    li { margin-bottom: 0.5rem; }
    blockquote {
      border-left: 4px solid #d1d5db;
      padding-left: 1rem;
      font-style: italic;
      margin: 1rem 0;
      color: #6b7280;
    }
    code {
      background-color: #f3f4f6;
      color: #1f2937;
      padding: 0.125rem 0.375rem;
      border-radius: 0.25rem;
      font-family: 'Courier New', monospace;
      font-size: 0.875rem;
    }
    pre {
      background-color: #1f2937;
      color: #f3f4f6;
      padding: 1rem;
      border-radius: 0.5rem;
      overflow-x: auto;
      margin: 1rem 0;
    }
    pre code {
      background-color: transparent;
      color: #f3f4f6;
      padding: 0;
    }
    a {
      color: #3b82f6;
      text-decoration: underline;
    }
    a:hover {
      color: #2563eb;
    }
    strong { font-weight: bold; }
    em { font-style: italic; }
    mark {
      background-color: #fef08a;
      padding: 0.125rem;
      border-radius: 0.125rem;
    }
    img {
      max-width: 100%;
      height: auto;
      border-radius: 0.5rem;
      margin: 1rem 0;
    }
    hr {
      border: none;
      border-top: 1px solid #d1d5db;
      margin: 2rem 0;
    }
  </style>
</head>
<body>
  ${content}
</body>
</html>`

    // Create blob and download
    const blob = new Blob([htmlDocument], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${fileName}.html`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting to HTML:', error)
    throw new Error('Failed to export to HTML')
  }
}

/**
 * Export document content to DOCX (placeholder - requires backend)
 * For now, this exports as HTML which can be opened in Word
 */
export function exportToDOCX(content: string, fileName: string): void {
  try {
    // Create a Word-compatible HTML document
    const docxHtml = `
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
  <meta charset='utf-8'>
  <title>${fileName}</title>
  <!--[if gte mso 9]>
  <xml>
    <w:WordDocument>
      <w:View>Print</w:View>
      <w:Zoom>100</w:Zoom>
      <w:DoNotOptimizeForBrowser/>
    </w:WordDocument>
  </xml>
  <![endif]-->
  <style>
    body { font-family: Calibri, sans-serif; font-size: 11pt; line-height: 1.5; }
    h1 { font-size: 16pt; font-weight: bold; margin-bottom: 10pt; }
    h2 { font-size: 14pt; font-weight: bold; margin-bottom: 8pt; margin-top: 12pt; }
    h3 { font-size: 12pt; font-weight: bold; margin-bottom: 6pt; margin-top: 10pt; }
    p { margin-bottom: 10pt; }
    ul, ol { margin-left: 20pt; margin-bottom: 10pt; }
    blockquote { border-left: 3pt solid #ddd; padding-left: 10pt; font-style: italic; margin: 10pt 0; }
    code { font-family: 'Courier New', monospace; background-color: #f0f0f0; padding: 2pt 4pt; }
    pre { background-color: #f5f5f5; padding: 10pt; border-radius: 5pt; }
  </style>
</head>
<body>
  ${content}
</body>
</html>`

    // Create blob and download as .doc (Word-compatible HTML)
    const blob = new Blob(['\ufeff', docxHtml], {
      type: 'application/msword',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${fileName}.doc`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting to DOCX:', error)
    throw new Error('Failed to export to DOCX')
  }
}

/**
 * Copy document content to clipboard
 */
export async function copyToClipboard(content: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(content)
  } catch (error) {
    console.error('Error copying to clipboard:', error)
    throw new Error('Failed to copy to clipboard')
  }
}
