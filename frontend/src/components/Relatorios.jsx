import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileText, FileDown, Download } from 'lucide-react';

const Relatorios = () => {
  const [tipoRelatorio, setTipoRelatorio] = useState('inventario');
  const [formato, setFormato] = useState('pdf');

  const exportarRelatorio = () => {
    const url = `/api/relatorios/${tipoRelatorio}/exportar?formato=${formato}`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Relatórios</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Tipo de Relatório</label>
              <Select value={tipoRelatorio} onValueChange={setTipoRelatorio}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="inventario">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 mr-2" />
                      Inventário Completo
                    </div>
                  </SelectItem>
                  <SelectItem value="posicao-estoque">Posição de Estoque</SelectItem>
                  <SelectItem value="movimentacoes">Movimentações</SelectItem>
                  <SelectItem value="estoque-baixo">Estoque Baixo</SelectItem>
                  <SelectItem value="estoque-alto">Estoque Alto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Formato</label>
              <Select value={formato} onValueChange={setFormato}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="mt-6">
            <Button onClick={exportarRelatorio} className="w-full md:w-auto">
              <Download className="h-4 w-4 mr-2" />
              Exportar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Relatorios;