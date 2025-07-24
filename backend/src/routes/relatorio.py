from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from src.models.material import Material, db
from src.models.movimentacao import Movimentacao
from src.models.user import User

relatorio_bp = Blueprint('relatorio', __name__)

@relatorio_bp.route('/relatorios/inventario', methods=['GET'])
@jwt_required()
def relatorio_inventario():
    """Relatório completo de inventário"""
    try:
        # Filtros opcionais
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        
        materiais = Material.query.filter_by(ativo=ativo).all()
        
        inventario = []
        valor_total = 0
        
        for material in materiais:
            valor_estoque = material.valor_total_estoque()
            valor_total += valor_estoque
            
            inventario.append({
                'material': material.to_dict(),
                'valor_estoque': valor_estoque
            })
        
        # Estatísticas gerais
        total_materiais = len(materiais)
        materiais_baixo_estoque = len([m for m in materiais if m.get_status_estoque() == 'baixo'])
        materiais_alto_estoque = len([m for m in materiais if m.get_status_estoque() == 'alto'])
        
        return jsonify({
            'inventario': inventario,
            'resumo': {
                'total_materiais': total_materiais,
                'valor_total_estoque': valor_total,
                'materiais_baixo_estoque': materiais_baixo_estoque,
                'materiais_alto_estoque': materiais_alto_estoque
            },
            'data_geracao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/posicao-estoque', methods=['GET'])
@jwt_required()
def relatorio_posicao_estoque():
    """Relatório de posição atual do estoque"""
    try:
        materiais = Material.query.filter_by(ativo=True).all()
        
        posicao = []
        for material in materiais:
            posicao.append({
                'id': material.id,
                'nome': material.nome,
                'codigo_barras': material.codigo_barras,
                'estoque_atual': material.estoque_atual,
                'estoque_minimo': material.estoque_minimo,
                'estoque_maximo': material.estoque_maximo,
                'status': material.get_status_estoque(),
                'localizacao': material.localizacao,
                'unidade_medida': material.unidade_medida,
                'valor_unitario': float(material.preco_custo) if material.preco_custo else 0.00,
                'valor_total': material.valor_total_estoque()
            })
        
        return jsonify({
            'posicao_estoque': posicao,
            'data_geracao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/relatorios/movimentacoes', methods=['GET'])
@jwt_required()
def relatorio_movimentacoes():
    """Relatório de movimentações por período"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        material_id = request.args.get('material_id', type=int)
        tipo = request.args.get('tipo', '')
        
        # Query base
        query = Movimentacao.query
        
        # Filtros de data (padrão: últimos 30 dias)
        if not data_inicio:
            data_inicio = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not data_fim:
            data_fim = datetime.utcnow().isoformat()
        
        data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
        data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
        
        query = query.filter(
            Movimentacao.data_movimentacao >= data_inicio_dt,
            Movimentacao.data_movimentacao <= data_fim_dt
        )
        
        # Outros filtros
        if material_id:
            query = query.filter_by(material_id=material_id)
        if tipo:
            query = query.filter_by(tipo_movimentacao=tipo)
        
        movimentacoes = query.order_by(desc(Movimentacao.data_movimentacao)).all()
        
        # Estatísticas
        total_entradas = sum(m.quantidade for m in movimentacoes if m.tipo_movimentacao == 'entrada')
        total_saidas = sum(m.quantidade for m in movimentacoes if m.tipo_movimentacao == 'saida')
        
        return jsonify({
            'movimentacoes': [mov.to_dict() for mov in movimentacoes],
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'resumo': {
                'total_movimentacoes': len(movimentacoes),
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_periodo': total_entradas - total_saidas
            },
            'data_geracao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/alertas/estoque-baixo', methods=['GET'])
@jwt_required()
def alertas_estoque_baixo():
    """Lista materiais com estoque baixo"""
    try:
        materiais_baixo = Material.query.filter(
            Material.ativo == True,
            Material.estoque_atual <= Material.estoque_minimo
        ).all()
        
        alertas = []
        for material in materiais_baixo:
            alertas.append({
                'material': material.to_dict(),
                'diferenca': material.estoque_minimo - material.estoque_atual,
                'percentual': (material.estoque_atual / material.estoque_minimo * 100) if material.estoque_minimo > 0 else 0
            })
        
        return jsonify({
            'alertas': alertas,
            'total_alertas': len(alertas),
            'data_verificacao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/alertas/estoque-alto', methods=['GET'])
@jwt_required()
def alertas_estoque_alto():
    """Lista materiais com estoque alto"""
    try:
        materiais_alto = Material.query.filter(
            Material.ativo == True,
            Material.estoque_atual >= Material.estoque_maximo
        ).all()
        
        alertas = []
        for material in materiais_alto:
            alertas.append({
                'material': material.to_dict(),
                'excesso': material.estoque_atual - material.estoque_maximo,
                'percentual': (material.estoque_atual / material.estoque_maximo * 100) if material.estoque_maximo > 0 else 0
            })
        
        return jsonify({
            'alertas': alertas,
            'total_alertas': len(alertas),
            'data_verificacao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorio_bp.route('/dashboard/metricas', methods=['GET'])
@jwt_required()
def dashboard_metricas():
    """Métricas principais para o dashboard"""
    try:
        # Contadores básicos
        total_materiais = Material.query.filter_by(ativo=True).count()
        materiais_baixo = Material.query.filter(
            Material.ativo == True,
            Material.estoque_atual <= Material.estoque_minimo
        ).count()
        materiais_alto = Material.query.filter(
            Material.ativo == True,
            Material.estoque_atual >= Material.estoque_maximo
        ).count()
        
        # Valor total do estoque
        materiais = Material.query.filter_by(ativo=True).all()
        valor_total_estoque = sum(material.valor_total_estoque() for material in materiais)
        
        # Movimentações recentes (últimos 7 dias)
        data_limite = datetime.utcnow() - timedelta(days=7)
        movimentacoes_recentes = Movimentacao.query.filter(
            Movimentacao.data_movimentacao >= data_limite
        ).count()
        
        # Top 5 materiais com mais movimentações
        top_materiais = db.session.query(
            Material.nome,
            func.count(Movimentacao.id).label('total_movimentacoes')
        ).join(Movimentacao).filter(
            Movimentacao.data_movimentacao >= data_limite
        ).group_by(Material.id, Material.nome).order_by(
            desc('total_movimentacoes')
        ).limit(5).all()
        
        return jsonify({
            'metricas': {
                'total_materiais': total_materiais,
                'materiais_baixo_estoque': materiais_baixo,
                'materiais_alto_estoque': materiais_alto,
                'valor_total_estoque': valor_total_estoque,
                'movimentacoes_recentes': movimentacoes_recentes
            },
            'top_materiais_movimentados': [
                {'nome': nome, 'movimentacoes': total} 
                for nome, total in top_materiais
            ],
            'data_atualizacao': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

