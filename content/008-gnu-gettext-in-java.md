Title: Использование GNU gettext в Java
Slug: gnu-gettext-in-java
Authors: Oleg Lomaka
Date: 2014-04-08 20:28
Category: blog
Tags: Java, GNU Gettext


### Введение в GNU gettext

Немного основ. Как работает GNU gettext и чем он лучше традиционных способов локализации в Java таких как <code>.properties</code> файлы.

 * Во-первых нормальная поддержка plural form. В неанглийском языке нереально перевести какие-то сложные предложения с числительными. Единственный способ изобретать свои
велосипеды при помощи [ChoiceFormat](http://docs.oracle.com/javase/8/docs/api/java/text/ChoiceFormat.html). Выглядят такие переводы нереально дико.
 * Во-вторых в исходном коде будут нормальные тексты, а не загадочные сокращения вроде <code>template.loginForm.okButtonLabel</code>.

К недостаткам можно отнести необходимость использовать сторонние утилиты, что не очень приветствуется в Java мире.
К счастью, эти утилиты должны использоваться только на этапе разработки/сборки пакета.
Они не нужны на продакшн-сервере или клиентской машине.

Итак, что это за утилиты и как их использовать. Процесс подготовки перевода можно разделить на несколько частей.

 1. Как-нибудь обозначить строки, подлежащие переводу в исходном коде. Традиционно функция, которая возвращает перевод строки называется просто символом подчеркивания <code>_</code> (это алиас полного названия <code>gettext</code>). Другие варианты <code>ngettext</code> (перевод фраз, зависящих от цифры), <code>pgettext</code> (фразы, имеющие разный перевод в разном контексте) и <code>npgettext</code> (ngettext & pgettext в одном). Вызов этих функций является своеобразным маркером того, что строки, переданные в качестве аргументов, подлежат переводу.
 1. Следующим шагом мы должны собрать все помеченные строки в одном <code>.pom</code> файле. Занимается этим утилита <code>xgettext</code>.
 1. Далее этот файл используется чтоб создать <code>.po</code> файл с переводом на конкретный язык. Для этого используются <code>msginit</code> & <code>msgmerge</code>.
 1. И последнее, нужно _откомпилировать_ <code>.po</code> файл с переводом в формат, который понимает наша программа. В мире C++/Python и других языков, которые используют нативные сишные библиотеки, компиляция происходит в <code>.mo</code> файл специального бинарного формата. Для Java мы должны откомпилировать либо в <code>.properties</code> файл, либо сразу в <code>.class</code>. В <code>.properties</code> смысла компилировать я не вижу, т.к. мы получим все те-же проблемы с невозможностью использования plural forms. В <code>.class</code> переводы компилируются утилитой <code>msgfmt</code>.

Теперь рассмотрим все эти шаги более подробно

### Маркировка строк для перевода

Про разные способы организации вызова фукнций, осуществляющих перевод, из кода можно почитать [здесь](http://www.gnu.org/software/gettext/manual/html_node/Java.html).

Для доступа к переводам, используется стандартный [ResourceBundle](http://docs.oracle.com/javase/8/docs/api/java/util/ResourceBundle.html) из поставки JDK.

### Создание <code>.pot</code> каталога строк, подлежащих перводу

Теперь мы должны найти все строки, нуждающиеся в переводе и сложить их в одном месте, так называемом словаре. Для этого существует утилита <code>xgettext</code>. Она принимает на вход имена файлов в которых нужно искать строки и складывает их в заданном месте. <code>xgettext</code> понимает большое кол-во языков, в том числе и Java.

Назовем наш словарь <code>messages.pot</code> и положем в <code>src/main/locale</code>.

    :::bash
	find . -name "*.java" | xgettext -D . -f - -o - > src/main/locale/messages.pot

Теперь у нас в <code>src/main/locale/messages.pot</code> будут храниться все строки, найденные в наших файлах с исходным кодом. Трогать этот файл не нужно. Его мы будет использовать для генерации <code>.po</code> файлов, которые будем редактировать.

### Создание <code>.po</code> файла перевода под конкретный язык

Каждый язык имеет какие-то свои правила при склонениях разных слов и фраз. Например в русском это "1 обезьяна", "2 обезьяны", "5 обезьян". GNU gettext знает все эти тонкости переводов и подготавливает вам файлик специальным образом чтоб мы могли правильно перевести все эти нюансы. Для работы с <code>.po</code> есть две команды: _msginit_ и _msgmerge_. Первая создает файлы, вторая их обновляет.

Создадим файл пеервода для русского языка

    :::bash
    msginit -l ru -i src/main/locale/messages.pot -o src/main/locale/messages_ru.po

После того, как мы его создали, можем немного подправить заголовок. В частности, поскольку мы собираемся туда писать русские буквы, нужно content-type поменять с ascii на utf-8

    :::makefile
	"Content-Type: text/plain; charset=UTF-8\n"

_msginit_ нужно выполнять только один раз, т.к. она перезапишет файл. В будующем, когда мы поменяем наши исходные коды и добавим/изменим строки перевода, нужно снова выполнить _xgettext_ из прошлого пункта и в этот раз запустить _msgmerge_ для обновления наших переводов. _msgmerge_ добавит отсутствующие строки в <code>.po</code> файл. Если же вы поменяли строку, то _msgmerge_ пометит перевод как fuzzy и не будет его использовать. Вам нужно после обновления проверять все fuzzy строки и удалять слово fuzzy после проверки перевода чтоб все работало. 

    :::bash
    msgmerge -U --lang=ru src/main/locale/messages_ru.po src/main/locale/messages.pot

### Компиляция <code>.po</code> файла перевода в java-class

После подготовки переводов, мы должны откомпилировать их в ресурсы, доступные нашей программе во время воплнения. Если у вас maven проект, то при стандарной directory layout ресурсы хранятся в src/main/resources. Один из файлов перевода мы должны сделать используемым по умолчанию, иначе будет ошибка, что попытаться запустить программу в локале для которой отсутствует перевод. Предположим у нас два перевода для испанского и русского языков. И мы хотим русский использовать по умолчанию. Тогда мы должны выполнить следующие команды

    :::bash
	msgfmt --java2 -d src/main/resources -r 'example.messages' src/main/locale/messages_ru.po       # default
	msgfmt --java2 -d src/main/resources -r 'example.messages' -l es src/main/locale/messages_es.po # spanish

Здесь мы назвали ресурс <code>example.messages</code>. Это название важно далее мы будем использовать его в коде для доступа к этим ресурсам.

### Возвращаясь к пункту про маркировку

И самое важно, как должен выглядеть Java-код в котором мы размечаем строки. Как на рекомендует официальная документация по gettext for Java, мы можем сделать утилитный класс со статическими методами и использовать их чтоб получить перевод.

    :::java
	package example;

	import gnu.gettext.GettextResource;

	import java.util.Locale;
	import java.util.ResourceBundle;

	public class I18NUtils {
		private static ResourceBundle resource =
				ResourceBundle.getBundle("example.messages", Locale.getDefault());

		public static String gettext(String text) {
			return GettextResource.gettext(resource, text);
		}

		public static String _(String text) {
			return gettext(text);
		}

		public static String ngettext(String msgid, String msgid_plural, long n) {
			return GettextResource.ngettext(resource, msgid, msgid_plural, n);
		}
	}

Теперь когда нам требуется перевод мы можем делать

    :::java
	import static example.I18NUtils._;
	System.out.println(_("Hello World!"));

Что очень похоже на вызов gettext из C/C++ или Python.

К сожалению, вызов ngettext не так похож и слегка многословен. Мы можем использовать ngettext в паре с MessageFormat для форматирования сообщений.

    :::java
    import static example.I18NUtils.ngettext
    System.out.println(MessageFormat.format(
			ngettext(
					"Something random happened {0} time",
					"Something random happened {0} times",
					n
			),
			new Object[]{n}
	));

Исходный код примеров можно скачать на [github](https://github.com/olomix/java-i18n-example/). 


### Что есть из готовой автоматизации

Есть готовый проект [gettext-commons](https://code.google.com/p/gettext-commons/), который включает в себя интеграцию с Ant & Maven, что позволит упростить работу с gettext до вызова нескольких maven комманд. Можно ознакомиться с его [туториалом](https://code.google.com/p/gettext-commons/wiki/Tutorial) для оценки чего он умеет. 
