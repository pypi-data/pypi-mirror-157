## Recomendación UNSPSC
===============
El Código Estándar de Productos y Servicios de Naciones Unidas (Código UNSPSC, por sus siglas en inglés) implementado en el sistema de contratación pública de Colombia con la versión 14.08 es una metodología de codificación de productos y servicios que de forma clara y siguiendo un arreglo jerárquico de cuatro niveles, les permite a las entidades públicas estandarizar las diferentes adquisiciones requeridas y  permite que proveedores y demás actores del sistema de contratación pública identifiquen de manera sencilla la demanda de los compradores. Así mismo, facilita la implementación de modelos de optimización de compra (como el modelo de abastecimiento estratégico propuesto por la Subdirección de Estudios de Mercado y Abastecimiento Estratégico de la entidad), permite la generación de cubos de gasto y el cálculo de penetración de productos en el sistema de compra pública y, finalmente, es una herramienta bastante útil para la creación de instrumentos de agregación de demanda y acuerdos marco de precio.

Aquí encontrará una herramienta muy sencilla que le hace una recomendación del código apropiado desde el detalle del objeto contractual.

Installing
============

.. code-block:: bash

    pip install clas_unspsc

Usage
=====

.. code-block:: bash

    >>> from clas_unspsc import recomendador_int
    >>> recomendador_int()